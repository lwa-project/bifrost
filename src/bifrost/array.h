/*
 * Copyright (c) 2016-2021, The Bifrost Authors. All rights reserved.
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

/*! \file array.h
 *  \brief Multi-dimensional array structure and operations
 *
 *  This module defines the BFarray structure, which is the fundamental
 *  data container for Bifrost operations, along with data type definitions
 *  and basic array operations.
 */

#ifndef BF_ARRAY_H_INCLUDE_GUARD_
#define BF_ARRAY_H_INCLUDE_GUARD_

#include <bifrost/common.h>
#include <bifrost/memory.h>

#ifdef __cplusplus
extern "C" {
#endif

/*! Maximum number of dimensions for BFarray */
enum {
	BF_MAX_DIMS = 8
};
typedef enum BFdtype_ {
	BF_DTYPE_NBIT_BITS      = 0x0000FF,
	BF_DTYPE_TYPE_BITS      = 0x000F00,
	BF_DTYPE_VECTOR_BITS    = 0x0FF000, // Vector length is these bits + 1
	BF_DTYPE_VECTOR_BIT0    = 12,
	
	//BF_DTYPE_SIGNED_BIT     = TODO
	//BF_DTYPE_COMPLEX_BIT    = 0x1000,
	BF_DTYPE_COMPLEX_BIT    = 0x100000,
	
	BF_DTYPE_INT_TYPE       = 0x0000,
	BF_DTYPE_UINT_TYPE      = 0x0100, // TODO: Consider removing in favour of signed bit
	BF_DTYPE_FLOAT_TYPE     = 0x0200,
	BF_DTYPE_STRING_TYPE    = 0x0300, // TODO: Use this as fixed-length byte array of up to 255 bytes
	BF_DTYPE_STORAGE_TYPE   = 0x0400, // For load/store (used in transpose)
	
	BF_DTYPE_I1    =  1 | BF_DTYPE_INT_TYPE,
	BF_DTYPE_I2    =  2 | BF_DTYPE_INT_TYPE,
	BF_DTYPE_I4    =  4 | BF_DTYPE_INT_TYPE,
	BF_DTYPE_I8    =  8 | BF_DTYPE_INT_TYPE,
	BF_DTYPE_I16   = 16 | BF_DTYPE_INT_TYPE,
	BF_DTYPE_I32   = 32 | BF_DTYPE_INT_TYPE,
	BF_DTYPE_I64   = 64 | BF_DTYPE_INT_TYPE,
	
	BF_DTYPE_U1    =   1 | BF_DTYPE_UINT_TYPE,
	BF_DTYPE_U2    =   2 | BF_DTYPE_UINT_TYPE,
	BF_DTYPE_U4    =   4 | BF_DTYPE_UINT_TYPE,
	BF_DTYPE_U8    =   8 | BF_DTYPE_UINT_TYPE,
	BF_DTYPE_U16   =  16 | BF_DTYPE_UINT_TYPE,
	BF_DTYPE_U32   =  32 | BF_DTYPE_UINT_TYPE,
	BF_DTYPE_U64   =  64 | BF_DTYPE_UINT_TYPE,
	
	BF_DTYPE_F16   =  16 | BF_DTYPE_FLOAT_TYPE,
	BF_DTYPE_F32   =  32 | BF_DTYPE_FLOAT_TYPE,
	BF_DTYPE_F64   =  64 | BF_DTYPE_FLOAT_TYPE,
#if defined BF_FLOAT128_ENABLED && BF_FLOAT128_ENABLED
	BF_DTYPE_F128  = 128 | BF_DTYPE_FLOAT_TYPE,
#endif
	
	BF_DTYPE_CI1   =   1 | BF_DTYPE_INT_TYPE | BF_DTYPE_COMPLEX_BIT,
	BF_DTYPE_CI2   =   2 | BF_DTYPE_INT_TYPE | BF_DTYPE_COMPLEX_BIT,
	BF_DTYPE_CI4   =   4 | BF_DTYPE_INT_TYPE | BF_DTYPE_COMPLEX_BIT,
	BF_DTYPE_CI8   =   8 | BF_DTYPE_INT_TYPE | BF_DTYPE_COMPLEX_BIT,
	BF_DTYPE_CI16  =  16 | BF_DTYPE_INT_TYPE | BF_DTYPE_COMPLEX_BIT,
	BF_DTYPE_CI32  =  32 | BF_DTYPE_INT_TYPE | BF_DTYPE_COMPLEX_BIT,
	BF_DTYPE_CI64  =  64 | BF_DTYPE_INT_TYPE | BF_DTYPE_COMPLEX_BIT,
	
	BF_DTYPE_CF16  =  16 | BF_DTYPE_FLOAT_TYPE | BF_DTYPE_COMPLEX_BIT,
	BF_DTYPE_CF32  =  32 | BF_DTYPE_FLOAT_TYPE | BF_DTYPE_COMPLEX_BIT,
	BF_DTYPE_CF64  =  64 | BF_DTYPE_FLOAT_TYPE | BF_DTYPE_COMPLEX_BIT,
#if defined BF_FLOAT128_ENABLED && BF_FLOAT128_ENABLED
	BF_DTYPE_CF128 = 128 | BF_DTYPE_FLOAT_TYPE | BF_DTYPE_COMPLEX_BIT
#endif
} BFdtype;
/*
typedef struct BFdtype_info_ {
	int32_t nbit;
	int32_t type;
	int8_t  is_complex;
	int8_t  is_floating_point;
	char    name[8];
} BFdtype_info;

// TODO: Implement this
BFstatus bfTypeInfo(BFdtype dtype, BFdtype_info* info); {
	BF_ASSERT(info, BF_STATUS_INVALID_POINTER);
	info->nbit       = (dtype & BF_DTYPE_NBIT_BITS);
	info->type       = (dtype & BF_DTYPE_TYPE_BITS) >> 8; // TODO: Avoid magic number
	info->is_signed  = (dtype & BF_DTYPE_SIGNED_BIT);
	info->is_complex = (dtype & BF_DTYPE_COMPLEX_BIT);
	
	}
*/

/*! \brief Multi-dimensional array descriptor
 *
 *  BFarray is the fundamental data structure for Bifrost operations.
 *  It describes the memory layout, data type, and location of array data.
 */
typedef struct BFarray_ {
	void*    data;                 /*!< Pointer to array data */
	BFspace  space;                /*!< Memory space (system, cuda, etc.) */
	BFdtype  dtype;                /*!< Data type encoding */
	int      ndim;                 /*!< Number of dimensions (max BF_MAX_DIMS) */
	long     shape[BF_MAX_DIMS];   /*!< Shape in elements per dimension */ // Elements
	long     strides[BF_MAX_DIMS]; /*!< Strides in bytes per dimension */ // Bytes
	BFbool   immutable;            /*!< If true, data cannot be modified */
	//BFbool   big_endian; // TODO: Better to be 'native_endian' (or 'byteswap') instead?
	BFbool   big_endian;           /*!< If true, data is big-endian */ // TODO: Better to be 'native_endian' (or 'byteswap') instead?
	BFbool   conjugated;           /*!< If true, complex values are conjugated */
	// TODO: Consider this. It could potentially be used for alpha/beta
	//         in MatMul, and also for fixed-point numerics.
	//double scale;
	// TODO: Consider this. It could be used by bfMap.
	//const char* name;
} BFarray;

// Set space, dtype, ndim, shape
// Ret data, strides
/*! \p bfArrayMalloc allocates memory for an array
 *
 *  The caller must set space, dtype, ndim, and shape before calling.
 *  On success, data and strides are filled in.
 *
 *  \param array Array descriptor with space, dtype, ndim, shape set
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfArrayMalloc(BFarray* array);

/*! \p bfArrayFree releases memory allocated by bfArrayMalloc
 *
 *  \param array Array to free
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfArrayFree(const BFarray* array);

/*! \p bfArrayCopy copies data between arrays
 *
 *  Handles copying between different memory spaces (e.g., CPU to GPU).
 *
 *  \param dst Destination array
 *  \param src Source array
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfArrayCopy(const BFarray* dst,
                     const BFarray* src);

/*! \p bfArrayMemset fills array memory with a byte value
 *
 *  \param array Array to fill
 *  \param value Byte value to fill with
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfArrayMemset(const BFarray* array,
                       int            value);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_ARRAY_H_INCLUDE_GUARD_
