
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

from bifrost.libbifrost import _bf, _check, BifrostObject
from bifrost.ndarray import asarray
from bifrost.ndarray import ndarray

from typing import Optional

from bifrost import telemetry
telemetry.track_module()

class LinAlg(BifrostObject):
    """GPU-accelerated linear algebra operations using cuBLAS.

    LinAlg provides matrix multiplication and related operations
    optimized for Bifrost arrays on the GPU.

    Example:
        >>> linalg = LinAlg()
        >>> # C = 1.0 * A @ B + 0.0 * C
        >>> linalg.matmul(1.0, A, B, 0.0, C)
    """
    def __init__(self):
        """Create a new linear algebra context."""
        BifrostObject.__init__(self, _bf.bfLinAlgCreate, _bf.bfLinAlgDestroy)
    def matmul(self, alpha: float, a: Optional[ndarray], b: Optional[ndarray], beta: float, c: ndarray) -> ndarray:
        """Perform GPU-accelerated matrix multiplication.

        Computes one of the following depending on inputs:
        - ``c = alpha * a @ b + beta * c`` (if both a and b provided)
        - ``c = alpha * a @ a^H + beta * c`` (if b is None)
        - ``c = alpha * b^H @ b + beta * c`` (if a is None)

        where ``@`` is matrix product and ``^H`` is Hermitian transpose.

        Multi-dimensional semantics follow numpy.matmul: the last two
        dimensions represent the matrix, and all other dimensions are
        batch dimensions that are matched or broadcast between a and b.

        Args:
            alpha: Scalar multiplier for the product term.
            a: Left matrix operand, or None for b^H @ b form.
            b: Right matrix operand, or None for a @ a^H form.
            beta: Scalar multiplier for the existing c values.
            c: Output matrix (modified in-place).

        Returns:
            ndarray: The output matrix c.

        **Tensor semantics**::

            Input a:  [..., M, K], space = CUDA
            Input b:  [..., K, N], space = CUDA
            Output c: [..., M, N], space = CUDA

        Supported dtype combinations:
            - ci8 inputs -> cf32 output (requires GPU compute capability >= 5.0)
            - cf32 inputs -> cf32 output
            - cf64 inputs -> cf64 output
            - f32 inputs -> f32 output
            - f64 inputs -> f64 output

        Example:
            >>> linalg = LinAlg()
            >>> # Compute correlation matrix: C = X @ X^H
            >>> linalg.matmul(1.0, X, None, 0.0, C)
        """
        if alpha is None:
            alpha = 1.
        if beta is None:
            beta = 0.
        beta  = float(beta)
        alpha = float(alpha)
        a_array = asarray(a).as_BFarray() if a is not None else None
        b_array = asarray(b).as_BFarray() if b is not None else None
        c_array = asarray(c).as_BFarray()
        _check(_bf.bfLinAlgMatMul(self.obj,
                                  alpha,
                                  a_array,
                                  b_array,
                                  beta,
                                  c_array))
        return c
