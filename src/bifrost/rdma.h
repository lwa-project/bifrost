/*
 * Copyright (c) 2022-2026, The Bifrost Authors. All rights reserved.
 * Copyright (c) 2022-2026, The University of New Mexico. All rights reserved.
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

/*! \file rdma.h
 *  \brief RDMA data transfer for ring buffer spans
 *
 *  This module provides RDMA (Remote Direct Memory Access) operations
 *  for transferring ring buffer data between nodes with low latency.
 */

#ifndef BF_RDMA_H_INCLUDE_GUARD_
#define BF_RDMA_H_INCLUDE_GUARD_

#ifdef __cplusplus
extern "C" {
#endif

#include <bifrost/array.h>

typedef struct BFrdma_impl* BFrdma;

/*! \p bfRdmaCreate creates an RDMA connection
 *
 *  \param obj          Pointer to receive the RDMA handle
 *  \param fd           Socket file descriptor for the connection
 *  \param message_size Maximum message size in bytes
 *  \param is_server    Non-zero if this is the server side
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfRdmaCreate(BFrdma* obj,
                      int     fd,
                      size_t  message_size,
                      int     is_server);
BFstatus bfRdmaDestroy(BFrdma obj);

/*! \p bfRdmaSendHeader sends span header metadata
 *
 *  \param obj              The RDMA handle
 *  \param time_tag         Time tag for the span
 *  \param header_size      Size of header data in bytes
 *  \param header           Header data to send
 *  \param offset_from_head Offset from the ring head
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfRdmaSendHeader(BFrdma      obj,
                          BFoffset    time_tag,
                          BFsize      header_size,
                          const void* header,
                          BFoffset    offset_from_head);

/*! \p bfRdmaSendSpan sends span data
 *
 *  \param obj  The RDMA handle
 *  \param span Span data to send
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfRdmaSendSpan(BFrdma         obj,
                        BFarray const* span);

/*! \p bfRdmaReceive receives header and span data
 *
 *  \param obj              The RDMA handle
 *  \param time_tag         Pointer to receive time tag
 *  \param header_size      Pointer to receive header size
 *  \param offset_from_head Pointer to receive offset from head
 *  \param span_size        Pointer to receive span data size
 *  \param contents         Buffer to receive header and span data
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfRdmaReceive(BFrdma    obj,
                       BFoffset* time_tag,
                       BFsize*   header_size,
                       BFoffset* offset_from_head,
                       BFsize*   span_size,
                       void*     contents);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_RDMA_H_INCLUDE_GUARD_
