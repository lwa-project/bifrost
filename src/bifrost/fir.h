/*
 * Copyright (c) 2017-2026, The Bifrost Authors. All rights reserved.
 * Copyright (c) 2017-2026, The University of New Mexico. All rights reserved.
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

/*! \file fir.h
 *  \brief Finite Impulse Response (FIR) filtering
 *
 *  This module provides FIR filter operations with support for decimation.
 *  Filters maintain state between calls to support streaming data.
 */

#ifndef BF_FIR_H_INCLUDE_GUARD_
#define BF_FIR_H_INCLUDE_GUARD_

#include <bifrost/common.h>
#include <bifrost/memory.h>
#include <bifrost/array.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct BFfir_impl* BFfir;

/*! \p bfFirCreate allocates a new FIR filter plan
 *
 *  \param plan Pointer to receive the plan handle
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfFirCreate(BFfir* plan);

/*! \p bfFirInit initializes a FIR filter plan
 *
 *  Call with plan_storage=NULL to query required storage size.
 *  Call again with allocated storage to complete initialization.
 *
 *  \param plan              The FIR plan to initialize
 *  \param coeffs            Filter coefficients array
 *  \param decim             Decimation factor (1 for no decimation)
 *  \param space             Memory space for execution (system or cuda)
 *  \param plan_storage      Storage buffer, or NULL to query size
 *  \param plan_storage_size Pointer to storage size (in/out)
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfFirInit(BFfir          plan,
                   BFarray const* coeffs,
                   BFsize         decim,
                   BFspace        space,
                   void*          plan_storage,
                   BFsize*        plan_storage_size);
BFstatus bfFirSetStream(BFfir       plan,
                        void const* stream);
BFstatus bfFirSetCoeffs(BFfir          plan,
                        BFarray const* coeffs);
BFstatus bfFirResetState(BFfir plan);

/*! \p bfFirExecute applies the FIR filter to input data
 *
 *  \param plan The FIR plan
 *  \param in   Input array
 *  \param out  Output array (size reduced by decimation factor)
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfFirExecute(BFfir          plan,
                      BFarray const* in,
                      BFarray const* out);
BFstatus bfFirDestroy(BFfir plan);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_FIR_H_INCLUDE_GUARD_
