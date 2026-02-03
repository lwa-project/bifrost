/*
 * Copyright (c) 2016, The Bifrost Authors. All rights reserved.
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

#include <bifrost/array.h>
#include "assert.hpp"
#include "utils.hpp"
#include "trace.hpp"

#include <cassert>
#include <cstring>

BFstatus bfDtypeInfoCreate(BFdtype_info** info_ptr) {
	BF_ASSERT(info_ptr, BF_STATUS_INVALID_POINTER);
	BF_TRY_RETURN_ELSE(*info_ptr = new BFdtype_info(),
	                   *info_ptr = 0);
}

BFstatus bfDtypeInfo(BFdtype dtype, BFdtype_info* info_ptr) {
	BF_ASSERT(info_ptr, BF_STATUS_INVALID_POINTER);

	int type_bits = (dtype & BF_DTYPE_TYPE_BITS);

	info_ptr->nbit              = (dtype & BF_DTYPE_NBIT_BITS);
	info_ptr->type              = type_bits;
	info_ptr->is_signed         = (type_bits == BF_DTYPE_INT_TYPE || type_bits == BF_DTYPE_FLOAT_TYPE);
	info_ptr->is_floating_point = (type_bits == BF_DTYPE_FLOAT_TYPE);
	info_ptr->is_complex        = (dtype & BF_DTYPE_COMPLEX_BIT) ? 1 : 0;
	info_ptr->is_storage        = (type_bits == BF_DTYPE_STORAGE_TYPE);
	info_ptr->is_string         = (type_bits == BF_DTYPE_STRING_TYPE);
	
	char* name_ptr = info_ptr->name;
	int pos = 0;
	int vector_len = BF_DTYPE_VECTOR_LENGTH(dtype);
	if( vector_len > 1 ) {
		pos += sprintf(name_ptr + pos, "Vector<");
	}
	
	if( info_ptr->is_complex ) {
		name_ptr[pos++] = 'c';
	}
	if( info_ptr->is_floating_point ) {
		name_ptr[pos++] = 'f';
	} else if( info_ptr->is_string ) {
		name_ptr[pos++] = 's';
	} else if( info_ptr->is_signed ) {
		name_ptr[pos++] = 'i';
	} else {
		name_ptr[pos++] = 'u';
	}
	pos += sprintf(name_ptr + pos, "%d", info_ptr->nbit);
	
	if( vector_len > 1 ) {
		pos += sprintf(name_ptr + pos, ", %d>", vector_len);
	}
	
	if( info_ptr->is_storage ) {
		pos += sprintf(name_ptr + pos, " (storage)");
	}
	
	name_ptr[pos] = '\0';
	
	return BF_STATUS_SUCCESS;
}

BFstatus bfDtypeInfoDestroy(BFdtype_info* info_ptr) {
	BF_ASSERT(info_ptr, BF_STATUS_INVALID_HANDLE);
	delete info_ptr;
	return BF_STATUS_SUCCESS;
}


// Reads array->(space,dtype,ndim,shape), sets array->strides and
//   allocates array->data.
BFstatus bfArrayMalloc(BFarray* array) {
	BF_TRACE();
	BF_ASSERT(array, BF_STATUS_INVALID_POINTER);
	int d = array->ndim - 1;
	array->strides[d] = BF_DTYPE_NBYTE(array->dtype);
	for( ; d-->0; ) {
		array->strides[d] = array->strides[d+1] * array->shape[d+1];
	}
	BFsize size = array->strides[0] * array->shape[0];
	return bfMalloc(&array->data, size, array->space);
}

BFstatus bfArrayFree(const BFarray* array) {
	BF_TRACE();
	BF_ASSERT(array, BF_STATUS_INVALID_POINTER);
	BFstatus ret = bfFree(array->data, array->space);
	//array->data = 0;
	return ret;
}

BFstatus bfArrayCopy(const BFarray* dst,
                     const BFarray* src) {
	BF_TRACE();
	BF_ASSERT(dst, BF_STATUS_INVALID_POINTER);
	BF_ASSERT(src, BF_STATUS_INVALID_POINTER);
	BF_ASSERT(shapes_equal(dst, src),   BF_STATUS_INVALID_SHAPE);
	BF_ASSERT(dst->dtype == src->dtype, BF_STATUS_INVALID_DTYPE);
	
	// Try merging contiguous dims together to reduce memory layout complexity
	BFarray dst_flattened, src_flattened;
	unsigned long keep_dims_mask = 0;
	keep_dims_mask |= padded_dims_mask(dst);
	keep_dims_mask |= padded_dims_mask(src);
	flatten(dst, &dst_flattened, keep_dims_mask);
	flatten(src, &src_flattened, keep_dims_mask);
	dst = &dst_flattened;
	src = &src_flattened;
	
	int ndim = dst->ndim;
	long const* shape = &dst->shape[0];
	
	if( is_contiguous(src) && is_contiguous(dst) ) {
		long size_bytes = dst->strides[0] * dst->shape[0];
		return bfMemcpy(dst->data, dst->space,
		                src->data, src->space,
		                size_bytes);
	} else if( ndim == 1 || ndim == 2 ) {
		// Note: ndim == 1 here means a 1D array with a stride between elements
		long itemsize_bytes = BF_DTYPE_NBYTE(src->dtype);
		// Note: bfMemcpy2D doesn't support strides on the inner dimension, so
		//         we can't support transposed or fast-strided 2D arrays here.
		BF_ASSERT(!(ndim == 2 && dst->strides[1] != itemsize_bytes),
		          BF_STATUS_UNSUPPORTED_STRIDE);
		BF_ASSERT(!(ndim == 2 && src->strides[1] != itemsize_bytes),
		          BF_STATUS_UNSUPPORTED_STRIDE);
		long width_bytes = (ndim == 2 ? shape[1] : 1) * itemsize_bytes;
		return bfMemcpy2D(dst->data, dst->strides[0], dst->space,
		                  src->data, src->strides[0], src->space,
		                  width_bytes, shape[0]);
	} else {
		BF_FAIL("Supported bfArrayCopy array layout", BF_STATUS_UNSUPPORTED); // TODO: Should support the general case
	}
}
BFstatus bfArrayMemset(const BFarray* dst,
                       int            value) {
	BF_TRACE();
	BF_ASSERT(dst, BF_STATUS_INVALID_POINTER);
	BF_ASSERT((unsigned char)(value) == value, BF_STATUS_INVALID_ARGUMENT);
	
	// Squeeze contiguous dims together to reduce memory layout complexity
	BFarray dst_flattened;
	flatten(dst, &dst_flattened, padded_dims_mask(dst));
	dst = &dst_flattened;
	
	int ndim = dst->ndim;
	long const* shape = &dst->shape[0];
	
	if( is_contiguous(dst) ) {
		long size_bytes = dst->strides[0] * dst->shape[0];
		return bfMemset(dst->data, dst->space,
		                value, size_bytes);
	} else if( ndim == 1 || ndim == 2 ) {
		// Note: ndim == 1 here means a 1D array with a stride between elements
		long itemsize_bytes = BF_DTYPE_NBYTE(dst->dtype);
		// Note: bfMemset2D doesn't support strides on the inner dimension, so
		//         we can't support transposed or fast-strided 2D arrays here.
		BF_ASSERT(!(ndim == 2 && dst->strides[1] != itemsize_bytes),
		          BF_STATUS_UNSUPPORTED_STRIDE);
		long width_bytes = (ndim == 2 ? shape[1] : 1) * itemsize_bytes;
		return bfMemset2D(dst->data, dst->strides[0], dst->space,
		                  value, width_bytes, shape[0]);
	} else {
		BF_FAIL("Supported bfArrayMemset array layout", BF_STATUS_UNSUPPORTED); // TODO: Should support the general case
	}
}

