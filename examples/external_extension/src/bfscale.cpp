/*
 * Copyright (c) 2016-2026, The Bifrost Authors. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * * Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 * * Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in the
 *   documentation and/or other materials provided with the distribution.
 * * Neither the name of The Bifrost Authors nor the names of its
 *   contributors may be used to endorse or promote products derived
 *   from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
 * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "bfscale.h"
#include <cstddef>

// Extension version
#define BFSCALE_VERSION_MAJOR 1
#define BFSCALE_VERSION_MINOR 0

// Helper: compute total number of elements in array
static long get_total_elements(BFarray const* arr) {
    long total = 1;
    for (int i = 0; i < arr->ndim; ++i) {
        total *= arr->shape[i];
    }
    return total;
}

BFstatus bfScale(BFarray const* in, BFarray* out, float scale) {
    // Validate pointers
    if (!in || !out) {
        return BF_STATUS_INVALID_POINTER;
    }

    // Check data types (only float32 supported in this example)
    if (in->dtype != BF_DTYPE_F32 || out->dtype != BF_DTYPE_F32) {
        return BF_STATUS_UNSUPPORTED_DTYPE;
    }

    // Check memory space (only system memory supported in this example)
    if (in->space != BF_SPACE_SYSTEM || out->space != BF_SPACE_SYSTEM) {
        return BF_STATUS_UNSUPPORTED_SPACE;
    }

    // Check shapes match
    if (in->ndim != out->ndim) {
        return BF_STATUS_INVALID_SHAPE;
    }
    for (int i = 0; i < in->ndim; ++i) {
        if (in->shape[i] != out->shape[i]) {
            return BF_STATUS_INVALID_SHAPE;
        }
    }

    // Get data pointers
    float const* in_data = static_cast<float const*>(in->data);
    float* out_data = static_cast<float*>(out->data);

    // Compute total elements
    long n = get_total_elements(in);

    // Apply scaling
    for (long i = 0; i < n; ++i) {
        out_data[i] = in_data[i] * scale;
    }

    return BF_STATUS_SUCCESS;
}

BFstatus bfScaleGetVersion(int* major, int* minor) {
    if (major) *major = BFSCALE_VERSION_MAJOR;
    if (minor) *minor = BFSCALE_VERSION_MINOR;
    return BF_STATUS_SUCCESS;
}
