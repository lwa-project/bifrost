#!/usr/bin/env python
"""
Test script for the bfscale extension.

Run with: python test_bfscale.py
"""

import sys
import os
import numpy as np
import numpy.testing as npt

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from bfscale import scale, get_version


def test_version():
    """Test that we can get the extension version."""
    major, minor = get_version()
    print(f"bfscale version: {major}.{minor}")
    assert major >= 1
    assert minor >= 0


def test_scale_basic():
    """Test basic scaling operation."""
    input_data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    output_data = np.zeros_like(input_data)
    scale_factor = 2.5

    result = scale(input_data, output_data, scale_factor)

    expected = input_data * scale_factor
    npt.assert_array_almost_equal(output_data, expected)
    print("test_scale_basic: PASSED")


def test_scale_2d():
    """Test scaling with 2D array."""
    input_data = np.arange(12, dtype=np.float32).reshape(3, 4)
    output_data = np.zeros_like(input_data)
    scale_factor = 0.5

    scale(input_data, output_data, scale_factor)

    expected = input_data * scale_factor
    npt.assert_array_almost_equal(output_data, expected)
    print("test_scale_2d: PASSED")


def test_scale_negative():
    """Test scaling with negative factor."""
    input_data = np.array([1.0, -2.0, 3.0, -4.0], dtype=np.float32)
    output_data = np.zeros_like(input_data)
    scale_factor = -1.0

    scale(input_data, output_data, scale_factor)

    expected = input_data * scale_factor
    npt.assert_array_almost_equal(output_data, expected)
    print("test_scale_negative: PASSED")


def test_scale_inplace():
    """Test that input and output can be the same array."""
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    original = data.copy()
    scale_factor = 3.0

    scale(data, data, scale_factor)

    expected = original * scale_factor
    npt.assert_array_almost_equal(data, expected)
    print("test_scale_inplace: PASSED")


if __name__ == '__main__':
    print("Testing bfscale extension...")
    print("-" * 40)

    test_version()
    test_scale_basic()
    test_scale_2d()
    test_scale_negative()
    test_scale_inplace()

    print("-" * 40)
    print("All tests passed!")
