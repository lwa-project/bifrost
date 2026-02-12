
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

from bifrost.libbifrost import _bf, _th, _check
from bifrost.ndarray import asarray
from bifrost.ndarray import ndarray

from bifrost import telemetry
telemetry.track_module()

def reduce(idata: ndarray, odata: ndarray, op: str='sum') -> ndarray:
    """Apply a reduction operation along one or more axes.

    The output array should have the reduced dimensions set to size 1
    to indicate which axes to reduce over.

    Args:
        idata: Input array to reduce.
        odata: Output array with reduced dimensions set to 1.
        op: Reduction operation, one of:

            Basic reductions:
                - ``'sum'``: sum(x)
                - ``'mean'``: sum(x) / n
                - ``'min'``: min(x)
                - ``'max'``: max(x)
                - ``'stderr'``: sum(x) / sqrt(n)

            Power (magnitude-squared) reductions:
                - ``'pwrsum'``: sum(|x|^2)
                - ``'pwrmean'``: sum(|x|^2) / n
                - ``'pwrmin'``: min(|x|^2)
                - ``'pwrmax'``: max(|x|^2)
                - ``'pwrstderr'``: sum(|x|^2) / sqrt(n)

    Returns:
        ndarray: The output array (same as odata).

    **Tensor semantics**::

        Input:  [..., M, ...], dtype = any numeric type, space = CUDA
        Output: [..., 1, ...], dtype = any numeric type, space = CUDA

    Example:
        >>> # Sum over the last axis
        >>> odata = ndarray(shape=(N, 1), dtype='f32', space='cuda')
        >>> reduce(idata, odata, op='sum')
    """
    try:
        op = getattr(_th.BFreduce_enum, op)
    except AttributeError:
        raise ValueError("Invalid reduce op: " + str(op))
    _check(_bf.bfReduce(asarray(idata).as_BFarray(),
                        asarray(odata).as_BFarray(),
                        op))
    return odata
