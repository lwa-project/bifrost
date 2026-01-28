
# Copyright (c) 2016-2023, The Bifrost Authors. All rights reserved.
# Copyright (c) 2016, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of The Bifrost Authors nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Ring buffer implementation for streaming data between pipeline blocks.

This module provides the core ring buffer data structure used in Bifrost
pipelines. Ring buffers enable thread-safe, lock-free data flow between
processing blocks.

Terminology
-----------
The following terms are used throughout Bifrost (see Cranmer et al. 2017):

**Frame**
    A single element of a data stream, analogous to a video frame. Each frame
    is an N-dimensional array whose axes may represent time, frequency,
    polarization, etc. Frames are the fundamental unit of data in a ring.

**Sequence**
    A logically-independent interval of data flow, such as a single observation
    or scan. Sequences have metadata headers and contain multiple frames. When
    sequence boundaries are reached, blocks can update their processing state.

**Span**
    A contiguous interval of frames accessed by a block. Writers "reserve"
    spans to get write access, readers "acquire" spans for read access. Spans
    may overlap between consecutive reads to handle block boundaries.

**Gulp size**
    The number of bytes (or frames) read from a ring buffer in a single
    operation. This determines the processing granularity and memory access
    pattern. Larger gulps improve throughput but increase latency.

**Buffer factor**
    A multiplier applied to the gulp size to determine total ring buffer
    allocation. For example, buffer_factor=4 allocates 4x the gulp size,
    allowing the writer to stay ahead of readers. Default is 4.

**Ringlet**
    When data has time as the fastest-varying axis, multiple parallel sub-rings
    (ringlets) can be used within a single ring. Each ringlet handles one
    "time stream" independently, enabling efficient processing of interleaved
    multi-channel data.

**Guarantee**
    A read mode where the reader is guaranteed that its data won't be
    overwritten by the writer while being accessed. Without guarantee, readers
    may see corrupted data if they fall behind.

Threading and Asynchronicity Model
----------------------------------
Bifrost's asynchronicity is based on CPU threads each having their own CUDA
stream. Each pipeline block runs in its own thread, and GPU operations within
a thread are submitted to that thread's CUDA stream.

Key principles:

1. All GPU work within a CPU thread is synchronous with respect to that thread
2. GPU work is asynchronous between different CPU threads
3. Before releasing data to other threads (via ring buffer commits), a block
   must call ``device.stream_synchronize()`` to ensure GPU work completes
4. This pattern ensures correctness while maximizing parallelism

The pipeline infrastructure handles synchronization automatically for standard
blocks (see ``pipeline.py``).

Example
-------
Basic ring buffer usage::

    ring = Ring(space='cuda', name='my_ring')
    ring.resize(gulp_size, buffer_factor=4)

    # Writer thread
    with ring.begin_writing() as writer:
        with writer.begin_sequence('observation1', header=json.dumps(hdr)) as seq:
            for chunk in data_source:
                with seq.reserve(nbytes) as span:
                    span.data[...] = chunk

    # Reader thread
    for sequence in ring.read():
        for span in sequence.read(gulp_size):
            process(span.data)

See Also
--------
bifrost.pipeline : High-level pipeline and block infrastructure
bifrost.ring2 : Alternative ring implementation for pipeline blocks
"""

from bifrost.libbifrost import _bf, _check, _get, BifrostObject, _string2space, _space2string, EndOfDataStop
from bifrost.DataType import DataType
from bifrost.ndarray import ndarray, _address_as_buffer

import ctypes
import string
import numpy as np
from uuid import uuid4

from typing import List, Optional, Tuple, Union

from bifrost import telemetry
telemetry.track_module()

def _slugify(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    valid_chars = frozenset(valid_chars)
    return ''.join([c for c in name if c in valid_chars])

class Ring(BifrostObject):
    """A ring buffer for streaming data between pipeline blocks.

    Rings are the core data structure in Bifrost for passing data between
    processing blocks. They provide thread-safe, lock-free data flow with
    support for multiple readers and a single writer.

    A ring holds a stream of **frames** (N-dimensional arrays) organized into
    **sequences** (logically-independent data intervals). Writers reserve
    **spans** to write data, and readers acquire spans to read. The ring
    automatically manages memory to allow producers and consumers to operate
    at different rates.

    Args:
        space: Memory space for the ring buffer. One of:

            - ``'system'``: CPU memory (default)
            - ``'cuda'``: GPU memory
            - ``'cuda_host'``: Pinned CPU memory (faster GPU transfers)
            - ``'cuda_managed'``: Unified memory (accessible from CPU and GPU)

        name: Optional name for the ring. If None, a UUID is generated.
            Names are useful for debugging and connecting blocks.
        core: Optional CPU core affinity for memory allocation. Setting this
            can improve NUMA locality for high-throughput applications.

    Example:
        >>> ring = Ring(space='cuda', name='my_ring')
        >>> ring.resize(gulp_size=1024*1024, buffer_factor=4)
        >>> with ring.begin_writing() as writer:
        ...     with writer.begin_sequence('seq1') as seq:
        ...         # Write data to the ring
        ...         pass

    See Also:
        :meth:`resize`: Configure ring memory allocation
        :class:`RingWriter`: Context manager for writing sequences
        :class:`ReadSequence`: Context manager for reading sequences
    """
    def __init__(self, space: str='system', name: Optional[str]=None, core: Optional[int]=None):
        if name is None:
            name = str(uuid4())
        name = _slugify(name)
        space = _string2space(space)
        #self.obj = None
        #self.obj = _get(_bf.bfRingCreate(name=name, space=space), retarg=0)
        BifrostObject.__init__(
            self, _bf.bfRingCreate, _bf.bfRingDestroy, name.encode(), space)
        if core is not None:
            try:
                _check( _bf.bfRingSetAffinity(self.obj, 
                                              core) )
            except RuntimeError:
                pass
    def resize(self, contiguous_span: int, total_span: Optional[int]=None, nringlet: int=1,
               buffer_factor: int=4) -> None:
        """Resize the ring buffer memory allocation.

        This method configures the ring's memory layout based on the expected
        access pattern. The key parameter is ``contiguous_span`` (the "gulp
        size"), which determines how much data is processed in each operation.

        Args:
            contiguous_span: The **gulp size** in bytes - the minimum contiguous
                memory that must be available for each read/write span. This
                should match the amount of data your blocks process per
                iteration. Larger values improve throughput but increase latency.
            total_span: Total bytes to allocate for the ring buffer. If None,
                defaults to ``contiguous_span * buffer_factor``. Larger buffers
                allow the writer to get further ahead of readers.
            nringlet: Number of **ringlets** (independent parallel data streams)
                in the ring. Use ringlets when data has time as the fastest-
                varying axis and you need to process multiple time streams
                independently. Default is 1 (single stream).
            buffer_factor: The **buffer factor** multiplier applied to gulp size
                when ``total_span`` is not specified. Default is 4, meaning the
                ring can hold 4 gulps of data. Higher values provide more
                buffering for bursty workloads but use more memory.

        Note:
            The total memory allocated is ``total_span * nringlet``. For GPU
            rings, ensure sufficient device memory is available.

        Example:
            >>> # Allocate ring for 1MB gulps with 4x buffering
            >>> ring.resize(contiguous_span=1024*1024, buffer_factor=4)
            >>> # Allocate ring with 4 ringlets for interleaved time streams
            >>> ring.resize(contiguous_span=4096, nringlet=4, buffer_factor=8)
        """
        if total_span is None:
            total_span = contiguous_span * buffer_factor
        _check( _bf.bfRingResize(self.obj,
                                 contiguous_span,
                                 total_span,
                                 nringlet) )
    @property
    def name(self) -> str:
        n = _get(_bf.bfRingGetName, self.obj)
        return n.decode()
    @property
    def space(self) -> str:
        return _space2string(_get(_bf.bfRingGetSpace, self.obj))
    @property
    def core(self) -> int:
        return _get(_bf.bfRingGetAffinity, self.obj)
    #def begin_sequence(self, name, header="", nringlet=1):
    #    return Sequence(ring=self, name=name, header=header, nringlet=nringlet)
    #def end_sequence(self, sequence):
    #    return sequence.end()
    #def _lock(self):
    #    self._check( self.lib.bfRingLock(self.obj) );
    #def unlock(self):
    #    self._check( self.lib.bfRingUnlock(self.obj) );
    #def lock(self):
    #    return RingLock(self)
    def begin_writing(self) -> "RingWriter":
        """Begin writing to the ring buffer.

        Returns:
            RingWriter: A context manager for writing sequences to the ring.
        """
        return RingWriter(self)
    def _begin_writing(self):
        _check( _bf.bfRingBeginWriting(self.obj) )
    def end_writing(self) -> None:
        """Signal that writing to the ring has completed."""
        _check( _bf.bfRingEndWriting(self.obj) )
    def writing_ended(self) -> bool:
        """Check if writing to the ring has been completed.

        Returns:
            bool: True if end_writing() has been called on the ring.
        """
        return _get( _bf.bfRingWritingEnded, self.obj )
    def open_sequence(self, name: str, guarantee: bool=True) -> "ReadSequence":
        """Open a specific sequence by name for reading.

        Args:
            name: The name of the sequence to open.
            guarantee: If True, guarantee that data won't be overwritten
                while being read.

        Returns:
            ReadSequence: A context manager for reading the sequence.
        """
        return ReadSequence(self, name=name, guarantee=guarantee)
    def open_sequence_at(self, time_tag: int, guarantee: bool=True) -> "ReadSequence":
        """Open a sequence at or after a specific time tag.

        Args:
            time_tag: The time tag at which to open the sequence.
            guarantee: If True, guarantee that data won't be overwritten
                while being read.

        Returns:
            ReadSequence: A context manager for reading the sequence.
        """
        return ReadSequence(self, which='at', time_tag=time_tag, guarantee=guarantee)
    def open_latest_sequence(self, guarantee: bool=True) -> "ReadSequence":
        """Open the most recent sequence in the ring.

        Args:
            guarantee: If True, guarantee that data won't be overwritten
                while being read.

        Returns:
            ReadSequence: A context manager for reading the sequence.
        """
        return ReadSequence(self, which='latest', guarantee=guarantee)
    def open_earliest_sequence(self, guarantee: bool=True) -> "ReadSequence":
        """Open the oldest sequence still available in the ring.

        Args:
            guarantee: If True, guarantee that data won't be overwritten
                while being read.

        Returns:
            ReadSequence: A context manager for reading the sequence.
        """
        return ReadSequence(self, which='earliest', guarantee=guarantee)
    # TODO: Alternative name?
    def read(self, whence: str='earliest', guarantee: bool=True) -> "ReadSequence":
        """Iterate over all sequences in the ring.

        This is a generator that yields each sequence in the ring,
        automatically advancing to the next sequence when available.

        Args:
            whence: Where to start reading. One of 'earliest' or 'latest'.
            guarantee: If True, guarantee that data won't be overwritten
                while being read.

        Yields:
            ReadSequence: Each sequence in the ring.

        Example:
            >>> for sequence in ring.read():
            ...     for span in sequence.read(gulp_size):
            ...         process(span.data)
        """
        with ReadSequence(self, which=whence, guarantee=guarantee) as cur_seq:
            while True:
                try:
                    yield cur_seq
                    cur_seq.increment()
                except EndOfDataStop:
                    return

class RingWriter(object):
    """Context manager for writing to a ring buffer.

    RingWriter is used to write sequences of data to a ring. It should
    be used as a context manager to ensure proper cleanup.

    Args:
        ring: The Ring to write to.

    Example:
        >>> with ring.begin_writing() as writer:
        ...     with writer.begin_sequence('my_sequence') as seq:
        ...         with seq.reserve(1024) as span:
        ...             span.data[...] = my_data
    """
    def __init__(self, ring: Ring):
        self.ring = ring
        self.ring._begin_writing()
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.ring.end_writing()
    def begin_sequence(self, name: str="", time_tag: int=-1,
                       header: str="", nringlet: int=1) -> "WriteSequence":
        """Begin a new sequence in the ring.

        Args:
            name: Name for the sequence.
            time_tag: Time tag for the sequence start. Use -1 for auto.
            header: Metadata header (typically JSON) for the sequence.
            nringlet: Number of independent data streams in this sequence.

        Returns:
            WriteSequence: A context manager for writing data to the sequence.
        """
        return WriteSequence(ring=self.ring, name=name, time_tag=time_tag,
                             header=header, nringlet=nringlet)

class SequenceBase(object):
    """Python object for a ring's sequence (data unit)"""
    def __init__(self, ring: Ring):
        self._ring = ring
    @property
    def _base_obj(self):
        return ctypes.cast(self.obj, _bf.BFsequence)
    @property
    def ring(self) -> Ring:
        return self._ring
    @property
    def name(self) -> str:
        n = _get(_bf.bfRingSequenceGetName, self._base_obj)
        return n.decode()
    @property
    def time_tag(self) -> int:
        return _get(_bf.bfRingSequenceGetTimeTag, self._base_obj)
    @property
    def nringlet(self) -> int:
        return _get(_bf.bfRingSequenceGetNRinglet, self._base_obj)
    @property
    def header_size(self) -> int:
        return _get(_bf.bfRingSequenceGetHeaderSize, self._base_obj)
    @property
    def _header_ptr(self):
        return _get(_bf.bfRingSequenceGetHeader, self._base_obj)
    @property # TODO: Consider not making this a property
    def header(self) -> np.ndarray:
        size = self.header_size
        if size == 0:
            # WAR for hdr_buffer_ptr.contents crashing when size == 0
            hdr_array = np.empty(0, dtype=np.uint8)
            hdr_array.flags['WRITEABLE'] = False
            return hdr_array
        hdr_buffer = _address_as_buffer(self._header_ptr, size, readonly=True)
        hdr_array = np.frombuffer(hdr_buffer, dtype=np.uint8)
        hdr_array.flags['WRITEABLE'] = False
        return hdr_array

class WriteSequence(SequenceBase):
    """A writable sequence in a ring buffer.

    WriteSequence represents a single logical unit of data being written
    to a ring. It contains metadata (header) and the data itself.

    Args:
        ring: The Ring to write to.
        name: Name for the sequence.
        time_tag: Time tag for the sequence start.
        header: Metadata header for the sequence.
        nringlet: Number of independent data streams.
    """
    def __init__(self, ring: Ring, name: str="", time_tag: int=-1, header: str="", nringlet: int=1):
        SequenceBase.__init__(self, ring)
        # TODO: Allow header to be a string, buffer, or numpy array
        header_size = len(header)
        if isinstance(header, np.ndarray):
            header = header.ctypes.data
        elif isinstance(header, str):
            header = header.encode()
        #print("hdr:", header_size, type(header))
        name = str(name)
        offset_from_head = 0
        self.obj = _bf.BFwsequence()
        _check(_bf.bfRingSequenceBegin(
            self.obj,
            ring.obj,
            name.encode(),
            time_tag,
            header_size,
            header,
            nringlet,
            offset_from_head))
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.end()
    def end(self) -> None:
        offset_from_head = 0
        _check(_bf.bfRingSequenceEnd(self.obj, offset_from_head))
    def reserve(self, size: int, nonblocking: bool=False) -> "WriteSpan":
        """Reserve a span of bytes for writing.

        Args:
            size: Number of bytes to reserve.
            nonblocking: If True, return immediately if space is not available.

        Returns:
            WriteSpan: A context manager providing access to the reserved memory.
        """
        return WriteSpan(self.ring, size, nonblocking)

class ReadSequence(SequenceBase):
    """A readable sequence in a ring buffer.

    ReadSequence provides access to a sequence of data written to a ring.
    It supports iterating through the data in spans (chunks).

    Args:
        ring: The Ring to read from.
        which: How to select the sequence. One of 'specific', 'latest',
            'earliest', or 'at'.
        name: Name of sequence (for which='specific').
        time_tag: Time tag (for which='at').
        other_obj: Reserved for internal use.
        guarantee: If True, guarantee data won't be overwritten while reading.
    """
    def __init__(self, ring: Ring, which: str='specific', name: str="",
                 time_tag: Optional[int]=None, other_obj: Optional[SequenceBase]=None,
                 guarantee: bool=True):
        SequenceBase.__init__(self, ring)
        self._ring = ring
        self.obj = _bf.BFrsequence()
        if which == 'specific':
            _check(_bf.bfRingSequenceOpen(self.obj, ring.obj, name, guarantee))
        elif which == 'latest':
            _check(_bf.bfRingSequenceOpenLatest(self.obj, ring.obj, guarantee))
        elif which == 'earliest':
            _check(_bf.bfRingSequenceOpenEarliest(self.obj, ring.obj, guarantee))
        elif which == 'at':
            _check(_bf.bfRingSequenceOpenAt(self.obj, ring.obj, time_tag, guarantee))
        #elif which == 'next':
        #    self._check( self.lib.bfRingSequenceOpenNext(pointer(self.obj), other_obj) )
        else:
            raise ValueError("Invalid 'which' parameter; must be one of: 'specific', 'latest', 'earliest'")
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.close()
    def close(self) -> None:
        _check(_bf.bfRingSequenceClose(self.obj))
    #def __next__(self):
    #    return self.next()
    #def next(self):
    #    return ReadSequence(self._ring, which='next', other_obj=self.obj)
    def increment(self) -> None:
        """Advance to the next sequence in the ring.

        Raises:
            EndOfDataStop: If no more sequences are available.
        """
        _check(_bf.bfRingSequenceNext(self.obj))
    def acquire(self, offset: int, size: int) -> "ReadSpan":
        """Acquire a span of data for reading.

        Args:
            offset: Byte offset from the start of the sequence.
            size: Number of bytes to acquire.

        Returns:
            ReadSpan: A context manager providing access to the data.
        """
        return ReadSpan(self, offset, size)
    def read(self, span_size: int, stride: Optional[int]=None, begin: int=0) -> "ReadSpan":
        """Iterate over the sequence data in spans.

        Args:
            span_size: Size of each span in bytes.
            stride: Bytes to advance between spans. Defaults to span_size.
            begin: Byte offset to start reading from.

        Yields:
            ReadSpan: Each span of data in the sequence.
        """
        if stride is None:
            stride = span_size
        offset = begin
        while True:
            try:
                with self.acquire(offset, span_size) as ispan:
                    yield ispan
                offset += stride
            except EndOfDataStop:
                return

class SpanBase(object):
    """Base class for ring buffer spans (contiguous data chunks).

    A span represents a contiguous region of data in the ring buffer,
    providing array-like access to the underlying memory.
    """
    def __init__(self, ring: Ring, writeable: bool):
        self._ring = ring
        self.writeable = writeable
    @property
    def _base_obj(self):
        return ctypes.cast(self.obj, _bf.BFspan)
    @property
    def ring(self) -> Ring:
        return self._ring
    @property
    def size(self) -> int:
        return _get(_bf.bfRingSpanGetSize, self._base_obj)
    @property
    def stride(self) -> int:
        return _get(_bf.bfRingSpanGetStride, self._base_obj)
    @property
    def offset(self) -> int:
        return _get(_bf.bfRingSpanGetOffset, self._base_obj)
    @property
    def nringlet(self) -> int:
        return _get(_bf.bfRingSpanGetNRinglet, self._base_obj)
    @property
    def _data_ptr(self):
        return _get(_bf.bfRingSpanGetData, self._base_obj)
    @property
    def data(self) -> ndarray:
        return self.data_view()
    def data_view(self, dtype: Union[str,np.dtype]=np.uint8,
                  shape: Union[int,List[int],Tuple[int]]=-1) -> ndarray:
        """Get a view of the span data with specified dtype and shape.

        Args:
            dtype: Data type for the array view.
            shape: Desired shape for the array. Use -1 for default.

        Returns:
            ndarray: Array view of the span data.
        """
        itemsize = DataType(dtype).itemsize
        assert( self.size   % itemsize == 0 )
        assert( self.stride % itemsize == 0 )
        data_ptr = self._data_ptr
        span_size  = self.size
        nringlet   = self.nringlet
        # TODO: We should really map the actual ring memory space and index
        #         it with offset rather than mapping from the current pointer.
        _shape   = (nringlet, span_size // itemsize)
        strides = (self.stride, itemsize) if nringlet > 1 else None
        space   = self.ring.space
        
        data_array = ndarray(shape=_shape, strides=strides,
                             buffer=data_ptr, dtype=dtype,
                             space=space)

        # Note: This is a non-standard attribute
        #data_array.flags['SPACE'] = space
        if not self.writeable:
            data_array.flags['WRITEABLE'] = False
        if shape != -1:
            # TODO: Check that this still wraps the same memory
            data_array = data_array.reshape(shape)
        return data_array
    #@property
    #def sequence(self):
    #    return self._sequence

class WriteSpan(SpanBase):
    """A writable span of data in a ring buffer.

    WriteSpan provides write access to a reserved region of ring memory.
    Data written to the span is committed when the span is closed.

    Args:
        ring: The Ring this span belongs to.
        size: Size of the span in bytes.
        nonblocking: If True, fail immediately if space is not available.
    """
    def __init__(self,
                 ring: Ring,
                 size: int,
                 nonblocking: bool=False):
        SpanBase.__init__(self, ring, writeable=True)
        self.obj = _bf.BFwspan()
        _check(_bf.bfRingSpanReserve(self.obj, ring.obj, size, nonblocking))
        self.commit_size = size
    def commit(self, size: int) -> None:
        """Set the number of bytes to commit when the span closes.

        Args:
            size: Number of bytes to commit (must be <= reserved size).
        """
        self.commit_size = size
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.close()
    def close(self) -> None:
        _check(_bf.bfRingSpanCommit(self.obj, self.commit_size))

class ReadSpan(SpanBase):
    """A readable span of data in a ring buffer.

    ReadSpan provides read-only access to a region of ring data.

    Args:
        sequence: The ReadSequence this span belongs to.
        offset: Byte offset from the start of the sequence.
        size: Size of the span in bytes.
    """
    def __init__(self, sequence: ReadSequence, offset: int, size: int):
        SpanBase.__init__(self, sequence.ring, writeable=False)
        self.obj = _bf.BFrspan()
        _check(_bf.bfRingSpanAcquire(self.obj, sequence.obj, offset, size))
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.release()
    def release(self) -> None:
        """Release the span, allowing the ring to reclaim the memory."""
        _check(_bf.bfRingSpanRelease(self.obj))
