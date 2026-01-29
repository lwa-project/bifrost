/*
 * Copyright (c) 2019-2026, The Bifrost Authors. All rights reserved.
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

/*! \file packet_writer.h
 *  \brief Packet writing for various data formats
 *
 *  This module provides packet writing functionality for transmitting data
 *  over UDP sockets, Infiniband Verbs, or to disk files. It supports multiple
 *  packet formats including TBN, DRX, CHIPS, COR, and others.
 */

#ifndef BF_PACKET_WRITER_H_INCLUDE_GUARD_
#define BF_PACKET_WRITER_H_INCLUDE_GUARD_

#ifdef __cplusplus
extern "C" {
#endif

#include <bifrost/array.h>

// Header setup

/*! \name Header Setup
 *  Functions for creating and managing packet headers for writer objects.
 *  @{
 */

typedef struct BFheaderinfo_impl* BFheaderinfo;

/*! \p bfHeaderInfoCreate allocates a new header info object
 *
 *  \param obj Pointer to receive the header info handle
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfHeaderInfoCreate(BFheaderinfo* obj);
BFstatus bfHeaderInfoDestroy(BFheaderinfo obj);
BFstatus bfHeaderInfoSetNSrc(BFheaderinfo obj,
                             int          nsrc);
BFstatus bfHeaderInfoSetNChan(BFheaderinfo obj,
                              int          nchan);
BFstatus bfHeaderInfoSetChan0(BFheaderinfo obj,
                              int          chan0);
BFstatus bfHeaderInfoSetTuning(BFheaderinfo obj,
                               int          tuning);
BFstatus bfHeaderInfoSetGain(BFheaderinfo       obj,
                             unsigned short int gain);
BFstatus bfHeaderInfoSetDecimation(BFheaderinfo obj,
                                   unsigned int decimation);

/*! @} */

// Writer setup

/*! \name Writer Setup
 *  Functions for creating and managing packet writer objects.
 *  @{
 */

typedef struct BFpacketwriter_impl* BFpacketwriter;

/*! \p bfDiskWriterCreate creates a packet writer for disk output
 *
 *  \param obj    Pointer to receive the packet writer handle
 *  \param format Packet format string (e.g., "tbn", "drx", "chips", "cor")
 *  \param fd     Open file descriptor to write to
 *  \param core   CPU core affinity (-1 for none)
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfDiskWriterCreate(BFpacketwriter* obj,
                            const char*     format,
                            int             fd,
                            int             core);
/*! \p bfUdpTransmitCreate creates a UDP packet transmitter
 *
 *  \param obj    Pointer to receive the packet writer handle
 *  \param format Packet format string
 *  \param fd     Bound UDP socket file descriptor
 *  \param core   CPU core affinity (-1 for none)
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpTransmitCreate(BFpacketwriter* obj,
                             const char*     format,
                             int             fd,
                             int             core);
BFstatus bfUdpVerbsTransmitCreate(BFpacketwriter* obj,
                                  const char*     format,
                                  int             fd,
                                  int             core);
/*! \p bfPacketWriterDestroy releases a packet writer object
 *
 *  \param obj The packet writer object to destroy
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketWriterDestroy(BFpacketwriter obj);

/*! \p bfPacketWriterSetRateLimit sets the transmission rate limit
 *
 *  \param obj        The packet writer object
 *  \param rate_limit Maximum rate in bytes per second (0 for unlimited)
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketWriterSetRateLimit(BFpacketwriter obj,
                                    unsigned int rate_limit);

/*! \p bfPacketWriterResetRateLimitCounter resets the rate limiter state
 *
 *  \param obj The packet writer object
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketWriterResetRateLimitCounter(BFpacketwriter obj);

/*! \p bfPacketWriterResetCounter resets the packet counter
 *
 *  \param obj The packet writer object
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketWriterResetCounter(BFpacketwriter obj);

/*! \p bfPacketWriterSend writes array data as formatted packets
 *
 *  \param obj           The packet writer object
 *  \param info          Header info with metadata for packet headers
 *  \param seq           Starting sequence number
 *  \param seq_increment Sequence number increment between packets
 *  \param src           Starting source identifier
 *  \param src_increment Source identifier increment between packets
 *  \param in            Input array containing data to send
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketWriterSend(BFpacketwriter obj,
                            BFheaderinfo   info,
                            BFoffset       seq,
                            BFoffset       seq_increment,
                            BFoffset       src,
                            BFoffset       src_increment,
                            BFarray const* in);

/*! @} */

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_PACKET_WRITER_H_INCLUDE_GUARD_
