# External Bifrost Extension Example

This directory contains a minimal example of how to create a Bifrost extension
that lives outside the Bifrost source tree.

## Overview

The example implements a simple `bfScale` function that multiplies array
elements by a constant factor. While trivial, it demonstrates all the key
concepts:

- C header with Bifrost types (`BFarray`, `BFstatus`)
- C++ implementation that operates on `BFarray` data
- Makefile that uses `bifrost-config` to get compiler flags
- Python wrapper using ctypes and Bifrost helpers

## Prerequisites

Bifrost must be installed with `bifrost-config` in your PATH:

```bash
which bifrost-config
bifrost-config --version
```

## Building

```bash
# Show build configuration (useful for debugging)
make info

# Build the extension
make

# Run tests
make test

# Clean build artifacts
make clean
```

## Directory Structure

```
external_extension/
├── Makefile              # Build system using bifrost-config
├── README.md             # This file
├── src/
│   ├── bfscale.h         # C header (Bifrost API)
│   └── bfscale.cpp       # C++ implementation
├── python/
│   └── bfscale.py        # Python wrapper
└── test_bfscale.py       # Test script
```

## Using the Extension

After building, you can use the extension in Python:

```python
import numpy as np
import sys
sys.path.insert(0, 'python')

from bfscale import scale, get_version

# Check version
print(f"Extension version: {get_version()}")

# Create test data
input_data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
output_data = np.zeros_like(input_data)

# Apply scaling
scale(input_data, output_data, scale_factor=2.5)
print(output_data)  # [2.5, 5.0, 7.5, 10.0]
```

## Creating Your Own Extension

1. **Copy this directory** as a starting point
2. **Rename files** from `bfscale` to your extension name
3. **Edit the header** (`src/yourext.h`) to declare your functions
4. **Implement** your functions in `src/yourext.cpp`
5. **Update the Makefile** with your extension name
6. **Create Python wrappers** in `python/yourext.py`
7. **Build and test**

### Key Points

- Functions should take `BFarray*` pointers and return `BFstatus`
- Check `dtype` and `space` before operating on data
- Use `bifrost.libbifrost._check()` to convert status codes to exceptions
- Use `bifrost.ndarray.asarray()` to convert numpy arrays to BFarray

## CUDA Extensions

For CUDA extensions, the Makefile already checks for CUDA support:

```makefile
HAVE_CUDA := $(shell $(BIFROST_CONFIG) --have-cuda)
ifeq ($(HAVE_CUDA),yes)
  NVCC      := $(shell $(BIFROST_CONFIG) --nvcc)
  NVCCFLAGS := $(shell $(BIFROST_CONFIG) --nvccflags)
endif
```

Add rules for `.cu` files as needed.
