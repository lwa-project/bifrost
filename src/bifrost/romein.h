/*
 * Copyright (c) 2026, The Bifrost Authors. All rights reserved.
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

/*! \file romein.h
 *  \brief Romein convolutional gridding on GPU
 *
 *  This module implements the Romein gridding algorithm, which performs
 *  convolution-based gridding on GPU. It can be used for visibility
 *  gridding, MOFF imaging, and other applications requiring fast
 *  convolutional resampling onto a regular grid.
 */

#ifndef BF_ROMEIN_H_INCLUDE_GUARD_
#define BF_ROMEIN_H_INCLUDE_GUARD_

#include <bifrost/common.h>
#include <bifrost/memory.h>
#include <bifrost/array.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct BFromein_impl* BFromein;

/*! \p bfRomeinCreate allocates a new Romein gridding plan
 *
 *  \param plan Pointer to receive the plan handle
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfRomeinCreate(BFromein* plan);

/*! \p bfRomeinInit initializes a Romein gridding plan
 *
 *  \param plan      The plan to initialize
 *  \param positions Grid positions array (x, y, z coordinates)
 *  \param kernels   Convolution kernels array
 *  \param ngrid     Output grid size
 *  \param polmajor  If true, polarization is the slowest varying dimension
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfRomeinInit(BFromein       plan,
                      BFarray const* positions,
                      BFarray const* kernels,
                      BFsize         ngrid,
                      BFbool         polmajor);
BFstatus bfRomeinSetStream(BFromein    plan,
                           void const* stream);
BFstatus bfRomeinSetPositions(BFromein       plan,
                              BFarray const* positions);
BFstatus bfRomeinSetKernels(BFromein       plan,
                            BFarray const* kernels);

/*! \p bfRomeinExecute performs convolutional gridding
 *
 *  \param plan The Romein plan
 *  \param in   Input data to grid
 *  \param out  Output gridded data
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfRomeinExecute(BFromein       plan,
                         BFarray const* in,
                         BFarray const* out);
BFstatus bfRomeinDestroy(BFromein plan);

#ifdef __cplusplus
}
#endif

#endif // BF_ROMEIN_H_INCLUDE_GUARD
