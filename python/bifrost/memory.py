
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

from bifrost.libbifrost import _bf, _check, _get, _string2space
import ctypes

from typing import Any, List

from bifrost import telemetry
telemetry.track_module()

def space_accessible(space: str, from_spaces: List[str]) -> bool:
    """Check if data in a memory space is accessible from other spaces.

    Determines whether data stored in ``space`` can be directly accessed
    by code running in any of ``from_spaces`` without requiring an
    explicit copy operation.

    Args:
        space: The memory space where the data resides.
            One of 'system', 'cuda', 'cuda_host', or 'cuda_managed'.
        from_spaces: Memory spaces from which access is attempted,
            or 'any' to indicate access from any space.

    Returns:
        bool: True if data in ``space`` is accessible from ``from_spaces``.

    Example:
        >>> space_accessible('cuda_host', ['system'])  # True (pinned memory is CPU-accessible)
        >>> space_accessible('cuda', ['system'])  # False (GPU memory requires copy)
    """
    if from_spaces == 'any': # TODO: This is a little bit hacky
        return True
    from_spaces = set(from_spaces)
    if space in from_spaces:
        return True
    elif space == 'cuda_host':
        return 'system' in from_spaces
    elif space == 'cuda_managed':
        return 'system' in from_spaces or 'cuda' in from_spaces
    else:
        return False

def raw_malloc(size: int, space: str) -> int:
    """Allocate raw memory in the specified memory space.

    This is a low-level function. Prefer using ndarray for most use cases.

    Args:
        size: Number of bytes to allocate.
        space: Memory space for allocation. One of 'system', 'cuda',
            'cuda_host', or 'cuda_managed'.

    Returns:
        int: Pointer to the allocated memory.

    Raises:
        RuntimeError: If allocation fails.
    """
    ptr = ctypes.c_void_p()
    _check(_bf.bfMalloc(ptr, size, _string2space(space)))
    return ptr.value
def raw_free(ptr: int, space: str='auto'):
    """Free memory previously allocated with raw_malloc.

    Args:
        ptr: Pointer to memory to free.
        space: Memory space of the allocation. Use 'auto' to automatically
            detect the space.
    """
    _check(_bf.bfFree(ptr, _string2space(space)))
def raw_get_space(ptr: int) -> _bf.BFspace:
    """Get the memory space of an allocated pointer.

    Args:
        ptr: Pointer to query.

    Returns:
        BFspace: The memory space constant for this pointer.
    """
    return _get(_bf.bfGetSpace, ptr)

def alignment() -> int:
    """Get the memory alignment used by Bifrost allocations.

    Returns:
        int: The alignment in bytes (typically 4096 for page alignment).
    """
    ret, _ = _bf.bfGetAlignment()
    return ret
