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

/*! \file fft.h
 *  \brief GPU-accelerated Fast Fourier Transform functions
 *
 *  This module provides FFT functionality using cuFFT for GPU-accelerated
 *  transforms on Bifrost arrays.
 */

#ifndef BF_FFT_H_INCLUDE_GUARD_
#define BF_FFT_H_INCLUDE_GUARD_

#include <bifrost/common.h>
#include <bifrost/array.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct BFfft_impl* BFfft;

/*! \p bfFftCreate allocates a new FFT plan object
 *
 *  \param plan_ptr Pointer to receive the created plan handle
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfFftCreate(BFfft* plan_ptr);

/*! \p bfFftInit initializes an FFT plan for specific array dimensions
 *
 *  Transform modes based on input/output types:
 *  - complex, complex => forward/inverse FFT
 *  - real, complex    => real-to-complex FFT
 *  - complex, real    => complex-to-real inverse FFT
 *  - real, real       => ERROR
 *
 *  The plan can be reused for arrays with the same shape and strides.
 *
 *  \param plan             The FFT plan handle
 *  \param iarray           Input array (defines transform shape)
 *  \param oarray           Output array (defines result shape)
 *  \param ndim             Number of axes to transform
 *  \param axes             Array of axis indices to transform
 *  \param apply_fftshift   If true, shift zero-frequency to center
 *  \param tmp_storage_size Pointer to receive required workspace size in bytes
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfFftInit(BFfft          plan,
                   BFarray const* iarray,
                   BFarray const* oarray,
                   int            ndim,
                   int     const* axes,
                   BFbool         apply_fftshift,
                   size_t*        tmp_storage_size);

/*! \p bfFftExecute executes the FFT on the given arrays
 *
 *  Transform modes based on input/output types:
 *  - complex, complex => forward/inverse FFT
 *  - real, complex    => real-to-complex FFT
 *  - complex, real    => complex-to-real inverse FFT
 *  - real, real       => ERROR
 *
 *  \param plan             The initialized FFT plan
 *  \param iarray           Input data array
 *  \param oarray           Output data array
 *  \param inverse          If true, perform inverse FFT
 *  \param tmp_storage      Pointer to workspace memory, or NULL for auto-allocation
 *  \param tmp_storage_size Size of workspace in bytes (from bfFftInit)
 *  \return BF_STATUS_SUCCESS on success
 *  \note If tmp_storage is NULL, the library will allocate storage automatically
 */
BFstatus bfFftExecute(BFfft          plan,
                      BFarray const* iarray,
                      BFarray const* oarray,
                      BFbool         inverse,
                      void*          tmp_storage,
                      size_t         tmp_storage_size);

/*! \p bfFftDestroy releases an FFT plan and its resources
 *
 *  \param plan The FFT plan to destroy
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfFftDestroy(BFfft plan);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_FFT_H_INCLUDE_GUARD_
