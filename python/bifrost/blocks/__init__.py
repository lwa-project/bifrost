
# Copyright (c) 2016-2023, The Bifrost Authors. All rights reserved.
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

"""Pre-built pipeline blocks for common data processing operations.

This module provides ready-to-use blocks for building Bifrost pipelines.
Blocks are the fundamental processing units that read from input rings,
perform computation, and write to output rings (see Cranmer et al. 2017).

Data Sources
------------
read_sigproc
    Read SIGPROC filterbank or time series files.
read_guppi_raw
    Read GUPPI raw voltage files.
read_wav
    Read WAV audio files.
binary_read
    Read raw binary data files.
read_audio
    Capture live audio from a sound card (requires PortAudio).
read_psrdada
    Read from a PSRDADA shared memory buffer (requires psrdada).

Data Sinks
----------
write_sigproc
    Write SIGPROC filterbank or time series files.
write_wav
    Write WAV audio files.
binary_write
    Write raw binary data files.

Transform Blocks
----------------
copy
    Copy data between memory spaces (e.g., system to GPU).
transpose
    Reorder array axes.
fft
    Apply Fast Fourier Transform (GPU-accelerated).
fftshift
    Shift zero-frequency component to center.
detect
    Form polarization products (Stokes parameters, etc.).
quantize
    Change data precision with scaling.
unpack
    Unpack low-bit data to higher precision.
reduce
    Apply reduction operations (sum, mean, min, max) along axes.
fdmt
    Fast Dispersion Measure Transform for pulsar searching.
correlate
    Cross-correlate antenna signals.
convert_visibilities
    Convert between visibility formats.
scrunch
    Average data along one or more axes.
accumulate
    Accumulate (integrate) data over time.
reverse
    Reverse data along specified axes.
serialize, deserialize
    Convert data to/from serialized format.

Utility Blocks
--------------
print_header
    Print sequence headers for debugging.

Example
-------
A typical pipeline reads data, copies to GPU, processes, and writes output::

    import bifrost.blocks as blocks

    with Pipeline() as pipeline:
        data = blocks.read_sigproc(['input.fil'], gulp_nframe=4096)
        gpu_data = blocks.copy(data, space='cuda')
        fft_data = blocks.fft(gpu_data, axes=1)
        detected = blocks.detect(fft_data, mode='stokes')
        cpu_data = blocks.copy(detected, space='system')
        blocks.write_sigproc(cpu_data, path='output')
        pipeline.run()

See Also
--------
bifrost.pipeline : Base classes for creating custom blocks
"""

from bifrost.blocks.copy import copy, CopyBlock
from bifrost.blocks.transpose import transpose, TransposeBlock
from bifrost.blocks.reverse import reverse, ReverseBlock
from bifrost.blocks.fft import fft, FftBlock
from bifrost.blocks.fftshift import fftshift, FftShiftBlock
from bifrost.blocks.fdmt import fdmt, FdmtBlock
from bifrost.blocks.detect import detect, DetectBlock
from bifrost.blocks.guppi_raw import read_guppi_raw, GuppiRawSourceBlock
from bifrost.blocks.print_header import print_header, PrintHeaderBlock
from bifrost.blocks.sigproc import read_sigproc, SigprocSourceBlock
from bifrost.blocks.sigproc import write_sigproc, SigprocSinkBlock
from bifrost.blocks.scrunch import scrunch, ScrunchBlock
from bifrost.blocks.accumulate import accumulate, AccumulateBlock
from bifrost.blocks.binary_io import BinaryFileReadBlock, BinaryFileWriteBlock
from bifrost.blocks.binary_io import binary_read, binary_write
from bifrost.blocks.unpack import unpack, UnpackBlock
from bifrost.blocks.quantize import quantize, QuantizeBlock
from bifrost.blocks.wav import read_wav, WavSourceBlock
from bifrost.blocks.wav import write_wav, WavSinkBlock
from bifrost.blocks.serialize import serialize, SerializeBlock, deserialize, DeserializeBlock
from bifrost.blocks.reduce import reduce, ReduceBlock
from bifrost.blocks.correlate import correlate, CorrelateBlock
from bifrost.blocks.convert_visibilities import convert_visibilities, ConvertVisibilitiesBlock

try: # Avoid error if portaudio library not installed
    from bifrost.blocks.audio import read_audio, AudioSourceBlock
except (ImportError, OSError):
    pass

try: # Avoid error if psrdada library not installed
    from bifrost.blocks.psrdada import read_psrdada_buffer, PsrDadaSourceBlock
except (ImportError, OSError):
    pass
