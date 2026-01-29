/*
 * Copyright (c) 2016-2026, The Bifrost Authors. All rights reserved.
 * Copyright (c) 2016, NVIDIA CORPORATION. All rights reserved.
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

/*! \file memory.h
 *  \brief Memory space aware allocation and data transfer
 *
 *  This module provides memory management functions that work across
 *  different memory spaces (system RAM, CUDA device, CUDA pinned host,
 *  CUDA managed). Copy operations handle transfers between any spaces.
 */

#ifndef BF_MEMORY_H_INCLUDE_GUARD_
#define BF_MEMORY_H_INCLUDE_GUARD_

#include <bifrost/common.h>

#ifdef __cplusplus
extern "C" {
#endif

/*! \brief Memory space identifiers */
typedef enum BFspace_ {
	BF_SPACE_AUTO         = 0, /*!< Automatic space detection */
	BF_SPACE_SYSTEM       = 1, /*!< System memory (aligned_alloc) */
	BF_SPACE_CUDA         = 2, /*!< CUDA device memory (cudaMalloc) */
	BF_SPACE_CUDA_HOST    = 3, /*!< CUDA pinned host memory (cudaHostAlloc) */
	BF_SPACE_CUDA_MANAGED = 4  /*!< CUDA managed memory (cudaMallocManaged) */
} BFspace;

/*! \p bfMalloc allocates memory in the specified space
 *
 *  \param ptr   Pointer to receive the allocated memory
 *  \param size  Number of bytes to allocate
 *  \param space Memory space to allocate in
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfMalloc(void** ptr, BFsize size, BFspace space);
BFstatus bfFree(void* ptr, BFspace space);

/*! \p bfGetSpace determines the memory space of a pointer
 *
 *  \param ptr   Pointer to query
 *  \param space Pointer to receive the memory space
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfGetSpace(const void* ptr, BFspace* space);
const char* bfGetSpaceString(BFspace space);

/*! \p bfMemcpy copies data between memory spaces
 *
 *  Synchronous with respect to the host, asynchronous with respect to device.
 *
 *  \param dst       Destination pointer
 *  \param dst_space Destination memory space
 *  \param src       Source pointer
 *  \param src_space Source memory space
 *  \param count     Number of bytes to copy
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfMemcpy(void*       dst,
                  BFspace     dst_space,
                  const void* src,
                  BFspace     src_space,
                  BFsize      count);

/*! \p bfMemcpy2D copies 2D data between memory spaces
 *
 *  \param dst        Destination pointer
 *  \param dst_stride Destination row stride in bytes
 *  \param dst_space  Destination memory space
 *  \param src        Source pointer
 *  \param src_stride Source row stride in bytes
 *  \param src_space  Source memory space
 *  \param width      Width of each row in bytes
 *  \param height     Number of rows to copy
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfMemcpy2D(void*       dst,
                    BFsize      dst_stride,
                    BFspace     dst_space,
                    const void* src,
                    BFsize      src_stride,
                    BFspace     src_space,
                    BFsize      width,
                    BFsize      height);
BFstatus bfMemset(void*   ptr,
                  BFspace space,
                  int     value,
                  BFsize  count);
BFstatus bfMemset2D(void*   ptr,
                    BFsize  stride,
                    BFspace space,
                    int     value,
                    BFsize  width,
                    BFsize  height);

/*! \p bfGetAlignment returns the memory alignment used by bfMalloc
 *
 *  \return Alignment in bytes
 */
BFsize bfGetAlignment();

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_MEMORY_H_INCLUDE_GUARD_
