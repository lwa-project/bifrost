
# Copyright (c) 2019-2024, The Bifrost Authors. All rights reserved.
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

# **TODO: Write tests for this class

from bifrost.libbifrost import _bf, _th, _check, _get, BifrostObject
from bifrost.udp_socket import UDPSocket
from bifrost.ring import Ring
from bifrost.ring2 import Ring as Ring2

import ctypes
from functools import reduce
from io import IOBase

from typing import Optional, Union

from bifrost import telemetry
telemetry.track_module()

class PacketCaptureCallback(BifrostObject):
    """Callback handler for packet capture sequence events.

    PacketCaptureCallback allows custom handling of packet format-specific
    sequence initialization. Different packet formats (VDIF, TBN, DRX, etc.)
    have different callbacks for interpreting packet headers and setting
    up the data stream.

    Example:
        >>> callback = PacketCaptureCallback()
        >>> callback.set_vdif(my_vdif_handler)
        >>> capture = UDPCapture('vdif', sock, ring, ..., callback)
    """
    _ref_cache = {}
    def __init__(self):
        """Create a new packet capture callback object."""
        BifrostObject.__init__(
            self, _bf.bfPacketCaptureCallbackCreate, _bf.bfPacketCaptureCallbackDestroy)

    def set_simple(self, fnc):
        self._ref_cache['simple'] = _bf.BFpacketcapture_simple_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetSIMPLE(
               self.obj, self._ref_cache['simple']))

    def set_chips(self, fnc: _bf.BFpacketcapture_chips_sequence_callback):
        self._ref_cache['chips'] = _bf.BFpacketcapture_chips_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetCHIPS(
               self.obj, self._ref_cache['chips']))
    def set_snap2(self, fnc: _bf.BFpacketcapture_snap2_sequence_callback):
        self._ref_cache['snap2'] = _bf.BFpacketcapture_snap2_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetSNAP2(
               self.obj, self._ref_cache['snap2']))
    def set_ibeam(self, fnc: _bf.BFpacketcapture_ibeam_sequence_callback):
        self._ref_cache['ibeam'] = _bf.BFpacketcapture_ibeam_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetIBeam(
               self.obj, self._ref_cache['ibeam']))
    def set_pbeam(self, fnc: _bf.BFpacketcapture_pbeam_sequence_callback):
        self._ref_cache['pbeam'] = _bf.BFpacketcapture_pbeam_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetPBeam(
               self.obj, self._ref_cache['pbeam']))
    def set_cor(self, fnc: _bf.BFpacketcapture_cor_sequence_callback):
        self._ref_cache['cor'] = _bf.BFpacketcapture_cor_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetCOR(
               self.obj, self._ref_cache['cor']))
    def set_vdif(self, fnc: _bf.BFpacketcapture_vdif_sequence_callback):
        self._ref_cache['vdif'] = _bf.BFpacketcapture_vdif_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetVDIF(
               self.obj, self._ref_cache['vdif']))
    def set_tbn(self, fnc: _bf.BFpacketcapture_tbn_sequence_callback):
        self._ref_cache['tbn'] = _bf.BFpacketcapture_tbn_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetTBN(
               self.obj, self._ref_cache['tbn']))
    def set_drx(self, fnc: _bf.BFpacketcapture_drx_sequence_callback):
        self._ref_cache['drx'] = _bf.BFpacketcapture_drx_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetDRX(
            self.obj, self._ref_cache['drx']))
    def set_drx8(self, fnc: _bf.BFpacketcapture_drx8_sequence_callback):
        self._ref_cache['drx8'] = _bf.BFpacketcapture_drx8_sequence_callback(fnc)
        _check(_bf.bfPacketCaptureCallbackSetDRX8(
            self.obj, self._ref_cache['drx8']))

class _CaptureBase(BifrostObject):
    """Base class for packet capture implementations.

    Provides common methods for receiving and managing packet capture
    operations across different capture backends (UDP, Verbs, Disk).
    """
    @staticmethod
    def _flatten_value(value):
        try:
            value = reduce(lambda x,y: x*y, value, 1 if value else 0)
        except TypeError:
            pass
        return value
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.end()
    def recv(self) -> _th.BFcapture_enum:
        """Receive packets and write them to the ring buffer.

        Returns:
            BFcapture_enum: Status code indicating the result:
                - BF_CAPTURE_STARTED: New sequence started
                - BF_CAPTURE_CONTINUED: Data added to current sequence
                - BF_CAPTURE_CHANGED: Sequence parameters changed
                - BF_CAPTURE_NO_DATA: No data received (timeout)
                - BF_CAPTURE_INTERRUPTED: Capture was interrupted
                - BF_CAPTURE_ERROR: An error occurred
        """
        status = _bf.BFpacketcapture_status()
        _check(_bf.bfPacketCaptureRecv(self.obj, status))
        return status.value
    def flush(self):
        """Flush any buffered data to the ring."""
        _check(_bf.bfPacketCaptureFlush(self.obj))
    def end(self):
        """End the packet capture session."""
        _check(_bf.bfPacketCaptureEnd(self.obj))

class UDPCapture(_CaptureBase):
    """Capture UDP packets and write them to a ring buffer.

    UDPCapture receives UDP packets from a bound socket and organizes
    them into a ring buffer according to the specified packet format.

    Args:
        fmt: Packet format string (e.g., 'vdif', 'tbn', 'drx', 'chips').
        sock: Bound UDPSocket to receive packets from.
        ring: Ring buffer to write captured data to.
        nsrc: Number of sources (e.g., antennas, beams) expected.
        src0: First source index.
        max_payload_size: Maximum UDP payload size in bytes.
        buffer_ntime: Number of time samples to buffer.
        slot_ntime: Number of time samples per slot.
        sequence_callback: Callback for handling sequence events.
        core: Optional CPU core affinity for the capture thread.

    Example:
        >>> sock = UDPSocket()
        >>> sock.bind(Address('0.0.0.0', 4015))
        >>> with UDPCapture('vdif', sock, ring, ...) as cap:
        ...     while cap.recv() != BF_CAPTURE_INTERRUPTED:
        ...         pass
    """
    def __init__(self, fmt: str, sock: UDPSocket, ring: Union[Ring,Ring2],
                 nsrc: int, src0: int, max_payload_size: int, buffer_ntime: int,
                 slot_ntime: int, sequence_callback: PacketCaptureCallback,
                 core: Optional[int]=None):
        nsrc = self._flatten_value(nsrc)
        if core is None:
            core = -1
        BifrostObject.__init__(
            self, _bf.bfUdpCaptureCreate, _bf.bfPacketCaptureDestroy,
            fmt.encode(), sock.fileno(), ring.obj, nsrc, src0,
            max_payload_size, buffer_ntime, slot_ntime,
            sequence_callback.obj, core)

class UDPSniffer(_CaptureBase):
    """Sniff UDP packets in promiscuous mode.

    Similar to UDPCapture, but uses raw sockets to capture packets
    destined for any address, not just those addressed to this host.
    Requires elevated privileges.

    Args:
        fmt: Packet format string (e.g., 'vdif', 'tbn', 'drx').
        sock: UDPSocket configured for sniffing.
        ring: Ring buffer to write captured data to.
        nsrc: Number of sources expected.
        src0: First source index.
        max_payload_size: Maximum UDP payload size in bytes.
        buffer_ntime: Number of time samples to buffer.
        slot_ntime: Number of time samples per slot.
        sequence_callback: Callback for handling sequence events.
        core: Optional CPU core affinity for the capture thread.
    """
    def __init__(self, fmt: str, sock: UDPSocket, ring: Union[Ring,Ring2],
                 nsrc: int, src0: int, max_payload_size: int, buffer_ntime: int,
                 slot_ntime: int, sequence_callback: PacketCaptureCallback,
                 core: Optional[int]=None):
        nsrc = self._flatten_value(nsrc)
        if core is None:
            core = -1
        BifrostObject.__init__(
            self, _bf.bfUdpSnifferCreate, _bf.bfPacketCaptureDestroy,
            fmt.encode(), sock.fileno(), ring.obj, nsrc, src0,
            max_payload_size, buffer_ntime, slot_ntime,
            sequence_callback.obj, core)

class UDPVerbsCapture(_CaptureBase):
    """High-performance UDP capture using Infiniband Verbs.

    Uses Infiniband Verbs (RDMA) for kernel-bypass packet capture,
    providing higher throughput and lower latency than standard sockets.
    Requires Infiniband hardware and the ibverbs library.

    Args:
        fmt: Packet format string (e.g., 'vdif', 'tbn', 'drx').
        sock: UDPSocket for the capture.
        ring: Ring buffer to write captured data to.
        nsrc: Number of sources expected.
        src0: First source index.
        max_payload_size: Maximum UDP payload size in bytes.
        buffer_ntime: Number of time samples to buffer.
        slot_ntime: Number of time samples per slot.
        sequence_callback: Callback for handling sequence events.
        core: Optional CPU core affinity for the capture thread.
    """
    def __init__(self, fmt: str, sock: UDPSocket, ring: Union[Ring,Ring2],
                 nsrc: int, src0: int, max_payload_size: int, buffer_ntime: int,
                 slot_ntime: int, sequence_callback: PacketCaptureCallback,
                 core: Optional[int]=None):
        if core is None:
            core = -1
        BifrostObject.__init__(
            self, _bf.bfUdpVerbsCaptureCreate, _bf.bfPacketCaptureDestroy,
            fmt.encode(), sock.fileno(), ring.obj, nsrc, src0,
            max_payload_size, buffer_ntime, slot_ntime,
            sequence_callback.obj, core)

class DiskReader(_CaptureBase):
    """Read packet data from disk files.

    DiskReader reads packet-formatted data from files and writes it
    to a ring buffer, simulating live packet capture for offline
    processing or testing.

    Args:
        fmt: Packet format string (e.g., 'vdif', 'tbn', 'drx').
        fh: Open file handle to read from.
        ring: Ring buffer to write data to.
        nsrc: Number of sources in the file.
        src0: First source index.
        buffer_nframe: Number of frames to buffer.
        slot_nframe: Number of frames per slot.
        sequence_callback: Callback for handling sequence events.
        core: Optional CPU core affinity.

    Example:
        >>> with open('data.vdif', 'rb') as fh:
        ...     with DiskReader('vdif', fh, ring, ...) as reader:
        ...         while reader.recv() != BF_CAPTURE_NO_DATA:
        ...             pass
    """
    def __init__(self, fmt: str, fh: IOBase, ring: Union[Ring,Ring2],
                 nsrc: int, src0: int, buffer_nframe: int, slot_nframe: int,
                 sequence_callback: PacketCaptureCallback,
                 core: Optional[int]=None):
        nsrc = self._flatten_value(nsrc)
        if core is None:
            core = -1
        BifrostObject.__init__(
            self, _bf.bfDiskReaderCreate, _bf.bfPacketCaptureDestroy,
            fmt.encode(), fh.fileno(), ring.obj, nsrc, src0,
            buffer_nframe, slot_nframe,
            sequence_callback.obj, core)
        # Make sure we start in the same place in the file
        self.seek(fh.tell(), _bf.BF_WHENCE_SET)
    def seek(self, offset: int, whence: _th.BFwhence_enum=_bf.BF_WHENCE_CUR):
        """Seek to a position in the file.

        Args:
            offset: Byte offset to seek to.
            whence: Reference point (BF_WHENCE_SET, BF_WHENCE_CUR, BF_WHENCE_END).

        Returns:
            int: New file position.
        """
        position = ctypes.c_ulong(0)
        _check(_bf.bfPacketCaptureSeek(self.obj, offset, whence, position))
        return position.value
    def tell(self) -> int:
        """Get the current file position.

        Returns:
            int: Current byte offset in the file.
        """
        position = ctypes.c_ulong(0)
        _check(_bf.bfPacketCaptureTell(self.obj, position))
        return position.value
