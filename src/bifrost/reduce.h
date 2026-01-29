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

/*! \file reduce.h
 *  \brief Reduction operations for multi-dimensional arrays
 *
 *  This module provides functions for reducing arrays along dimensions
 *  using operations such as sum, mean, min, max, and power statistics.
 */

#ifndef BF_REDUCE_H_INCLUDE_GUARD_
#define BF_REDUCE_H_INCLUDE_GUARD_

#include <bifrost/common.h>
#include <bifrost/memory.h>
#include <bifrost/array.h>

#ifdef __cplusplus
extern "C" {
#endif

/*! \brief Reduction operations for bfReduce */
typedef enum BFreduce_op_ {
	BF_REDUCE_SUM,          /*!< sum(x) */
	BF_REDUCE_MEAN,         /*!< sum(x) / n */
	BF_REDUCE_MIN,          /*!< min(x) */
	BF_REDUCE_MAX,          /*!< max(x) */
	BF_REDUCE_STDERR,       /*!< sum(x) / sqrt(n) */
	BF_REDUCE_POWER_SUM,    /*!< sum(|x|^2) */
	BF_REDUCE_POWER_MEAN,   /*!< sum(|x|^2) / n */
	BF_REDUCE_POWER_MIN,    /*!< min(|x|^2) */
	BF_REDUCE_POWER_MAX,    /*!< max(|x|^2) */
	BF_REDUCE_POWER_STDERR, /*!< sum(|x|^2) / sqrt(n) */
} BFreduce_op;

/*! \p bfReduce reduces an array along collapsed dimensions
 *
 *  Dimensions with size 1 in the output are reduced from the input.
 *  The input and output arrays must have the same number of dimensions.
 *
 *  \param in  Input array to reduce
 *  \param out Output array (dimensions with size 1 are reduced)
 *  \param op  Reduction operation to apply
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfReduce(BFarray const* in, BFarray const* out, BFreduce_op op);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_REDUCE_H_INCLUDE_GUARD_
