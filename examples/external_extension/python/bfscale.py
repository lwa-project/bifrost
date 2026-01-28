"""
Python wrapper for the bfscale extension.

This module demonstrates how to wrap an external Bifrost C extension
using ctypes and Bifrost's helper utilities.
"""

import os
import ctypes
from ctypes import c_int, c_float, POINTER, byref

from bifrost.libbifrost import _check
from bifrost.ndarray import asarray
import bifrost.libbifrost_generated as _bf

# Find and load the extension library
# Look in the directory containing this file, then parent directory
_this_dir = os.path.dirname(os.path.abspath(__file__))
_lib_paths = [
    os.path.join(_this_dir, '..', 'libbfscale.so'),
    os.path.join(_this_dir, 'libbfscale.so'),
    'libbfscale.so',  # Fall back to LD_LIBRARY_PATH
]

_lib = None
for _path in _lib_paths:
    try:
        _lib = ctypes.CDLL(_path)
        break
    except OSError:
        continue

if _lib is None:
    raise ImportError(
        "Could not find libbfscale.so. "
        "Make sure to build it first with 'make' and either:\n"
        "  1. Run from the extension directory, or\n"
        "  2. Add the library path to LD_LIBRARY_PATH"
    )

# Set up function signatures
_lib.bfScale.argtypes = [
    POINTER(_bf.BFarray),  # in
    POINTER(_bf.BFarray),  # out
    c_float,               # scale
]
_lib.bfScale.restype = _bf.BFstatus

_lib.bfScaleGetVersion.argtypes = [
    POINTER(c_int),  # major
    POINTER(c_int),  # minor
]
_lib.bfScaleGetVersion.restype = _bf.BFstatus


def scale(input_array, output_array, scale_factor):
    """Scale array elements by a constant factor.

    Computes: output[i] = input[i] * scale_factor

    Args:
        input_array: Input array (numpy or bifrost ndarray, float32)
        output_array: Output array (same shape as input, float32)
        scale_factor: Multiplicative scale factor (float)

    Returns:
        The output array

    Raises:
        RuntimeError: If the operation fails (e.g., wrong dtype or space)
    """
    # Convert to bifrost arrays if needed
    in_arr = asarray(input_array)
    out_arr = asarray(output_array)

    # Call the C function
    _check(_lib.bfScale(
        in_arr.as_BFarray(),
        out_arr.as_BFarray(),
        float(scale_factor)
    ))

    return output_array


def get_version():
    """Get the extension version.

    Returns:
        Tuple of (major, minor) version numbers
    """
    major = c_int()
    minor = c_int()
    _check(_lib.bfScaleGetVersion(byref(major), byref(minor)))
    return (major.value, minor.value)
