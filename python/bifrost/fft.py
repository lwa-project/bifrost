
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

from bifrost.libbifrost import _bf, _th, _check, _get, BifrostObject
from bifrost.ndarray import asarray
from bifrost.ndarray import ndarray
import ctypes

from typing import List, Optional, Tuple, Union

from bifrost import telemetry
telemetry.track_module()

class Fft(BifrostObject):
    """GPU-accelerated Fast Fourier Transform using cuFFT.

    The Fft class provides a wrapper around cuFFT for performing FFTs
    on Bifrost ndarrays. It supports multi-dimensional transforms and
    various data type combinations.

    Example:
        >>> fft = Fft()
        >>> fft.init(input_array, output_array, axes=[0, 1])
        >>> fft.execute(input_array, output_array, inverse=False)
    """
    def __init__(self):
        """Create a new FFT plan object."""
        BifrostObject.__init__(self, _bf.bfFftCreate, _bf.bfFftDestroy)
    def init(self, iarray: ndarray, oarray: ndarray,
             axes: Optional[Union[int,List[int],Tuple[int]]]=None,
             apply_fftshift: bool=False):
        """Initialize the FFT plan for specific array dimensions.

        This must be called before execute(). The plan can be reused for
        arrays with the same shape and strides.

        Args:
            iarray: Input array specifying the transform dimensions.
            oarray: Output array specifying the result dimensions.
            axes: Axis or list of axes to transform. If None, all axes
                are transformed.
            apply_fftshift: If True, shift zero-frequency component to center.
                Equivalent to numpy.fft.fftshift on the output.

        Note:
            After calling init(), the required workspace size is available
            in ``self.workspace_size``.
        """
        if isinstance(axes, int):
            axes = [axes]
        ndim = len(axes)
        if axes is not None:
            axes_type = ctypes.c_int * ndim
            axes = axes_type(*axes)
        self.workspace_size = _get(_bf.bfFftInit,
                                   self.obj,
                                   asarray(iarray).as_BFarray(),
                                   asarray(oarray).as_BFarray(),
                                   ndim,
                                   axes,
                                   apply_fftshift)
    def execute(self, iarray: ndarray, oarray: ndarray, inverse: bool=False) -> ndarray:
        """Execute the FFT.

        Args:
            iarray: Input array containing data to transform.
            oarray: Output array to store the result.
            inverse: If True, perform the inverse FFT.

        Returns:
            ndarray: The output array (same as oarray).
        """
        return self.execute_workspace(iarray, oarray,
                                      workspace_ptr=None, workspace_size=0,
                                      inverse=inverse)
    def execute_workspace(self, iarray: ndarray, oarray: ndarray,
                          workspace_ptr: int, workspace_size: int,
                          inverse: bool=False) -> ndarray:
        """Execute the FFT with an external workspace.

        This allows reusing a workspace buffer across multiple FFT
        operations to reduce memory allocation overhead.

        Args:
            iarray: Input array containing data to transform.
            oarray: Output array to store the result.
            workspace_ptr: Pointer to workspace memory.
            workspace_size: Size of workspace in bytes.
            inverse: If True, perform the inverse FFT.

        Returns:
            ndarray: The output array (same as oarray).
        """
        _check(_bf.bfFftExecute(
            self.obj,
            asarray(iarray).as_BFarray(),
            asarray(oarray).as_BFarray(),
            inverse,
            workspace_ptr, workspace_size))
        return oarray
