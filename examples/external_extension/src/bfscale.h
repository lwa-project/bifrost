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

/*
 * Example Bifrost extension: bfScale
 *
 * Demonstrates how to create an external C extension that links against
 * libifrost and operates on BFarray data.
 */

#ifndef BFSCALE_H_INCLUDE_GUARD_
#define BFSCALE_H_INCLUDE_GUARD_

#include <bifrost/common.h>
#include <bifrost/array.h>

#ifdef __cplusplus
extern "C" {
#endif

/*! \brief Scale array elements by a constant factor
 *
 *  Computes: out[i] = in[i] * scale for all elements
 *
 *  \param in     Input array (must be float32)
 *  \param out    Output array (must be float32, same shape as input)
 *  \param scale  Scale factor to apply
 *  \return BF_STATUS_SUCCESS on success, error code otherwise
 */
BFstatus bfScale(BFarray const* in, BFarray* out, float scale);

/*! \brief Get the version of this extension
 *
 *  \param major  Pointer to store major version
 *  \param minor  Pointer to store minor version
 *  \return BF_STATUS_SUCCESS
 */
BFstatus bfScaleGetVersion(int* major, int* minor);

#ifdef __cplusplus
}
#endif

#endif // BFSCALE_H_INCLUDE_GUARD_
