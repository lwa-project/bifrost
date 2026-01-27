/*
 * Copyright (c) 2019-2023, The Bifrost Authors. All rights reserved.
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

/*! \file packet_capture.h
 *  \brief Packet capture for various data formats
 *
 *  This module provides packet capture functionality for receiving data
 *  from UDP sockets, Infiniband Verbs, or disk files. It supports multiple
 *  packet formats including VDIF, TBN, DRX, CHIPS, and others.
 */

#ifndef BF_PACKET_CAPTURE_H_INCLUDE_GUARD_
#define BF_PACKET_CAPTURE_H_INCLUDE_GUARD_

#ifdef __cplusplus
extern "C" {
#endif

#include <bifrost/io.h>
#include <bifrost/ring.h>

// Callback setup

/*! \name Sequence Callbacks
 *  Callback function types for handling sequence initialization
 *  for different packet formats.
 *  @{
 */

typedef int (*BFpacketcapture_simple_sequence_callback)(BFoffset, int, int, int,
                                                       BFoffset*, void const**, size_t*);
typedef int (*BFpacketcapture_chips_sequence_callback)(BFoffset, int, int, int,
                                                       BFoffset*, void const**, size_t*);
typedef int (*BFpacketcapture_snap2_sequence_callback)(BFoffset, int, int, int,
                                                       BFoffset*, void const**, size_t*);
typedef int (*BFpacketcapture_ibeam_sequence_callback)(BFoffset, int, int, int,
                                                       BFoffset*, void const**, size_t*);
typedef int (*BFpacketcapture_pbeam_sequence_callback)(BFoffset, BFoffset, int, int, int,
                                                       int, void const**, size_t*);
typedef int (*BFpacketcapture_cor_sequence_callback)(BFoffset, BFoffset, int, int,
                                                     int, int, void const**, size_t*);
typedef int (*BFpacketcapture_vdif_sequence_callback)(BFoffset, BFoffset, int, int, int,
                                                     int, int, int, void const**, size_t*);
typedef int (*BFpacketcapture_tbn_sequence_callback)(BFoffset, BFoffset, int, int, 
                                                     int, void const**, size_t*);
typedef int (*BFpacketcapture_drx_sequence_callback)(BFoffset, BFoffset, int, int, int, 
                                                     int, void const**, size_t*);
typedef int (*BFpacketcapture_drx8_sequence_callback)(BFoffset, BFoffset, int, int, int, 
                                                    int, void const**, size_t*);

/*! @} */

typedef struct BFpacketcapture_callback_impl* BFpacketcapture_callback;

/*! \p bfPacketCaptureCallbackCreate allocates a new callback object
 *
 *  \param obj Pointer to receive the callback handle
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketCaptureCallbackCreate(BFpacketcapture_callback* obj);
BFstatus bfPacketCaptureCallbackDestroy(BFpacketcapture_callback obj);
BFstatus bfPacketCaptureCallbackSetSIMPLE(BFpacketcapture_callback obj,
                                         BFpacketcapture_simple_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetCHIPS(BFpacketcapture_callback obj,
                                         BFpacketcapture_chips_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetSNAP2(BFpacketcapture_callback obj,
                                         BFpacketcapture_snap2_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetIBeam(BFpacketcapture_callback obj,
                                         BFpacketcapture_ibeam_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetPBeam(BFpacketcapture_callback obj,
                                         BFpacketcapture_pbeam_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetCOR(BFpacketcapture_callback obj,
                                       BFpacketcapture_cor_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetVDIF(BFpacketcapture_callback obj,
                                        BFpacketcapture_vdif_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetTBN(BFpacketcapture_callback obj,
                                       BFpacketcapture_tbn_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetDRX(BFpacketcapture_callback obj,
                                       BFpacketcapture_drx_sequence_callback callback);
BFstatus bfPacketCaptureCallbackSetDRX8(BFpacketcapture_callback obj,
                                       BFpacketcapture_drx8_sequence_callback callback);

// Capture setup

/*! \name Capture Setup
 *  Functions for creating and managing packet capture objects.
 *  @{
 */

typedef struct BFpacketcapture_impl* BFpacketcapture;

/*! \brief Status codes returned by packet capture operations */
typedef enum BFpacketcapture_status_ {
        BF_CAPTURE_STARTED,     /*!< New sequence started */
        BF_CAPTURE_ENDED,       /*!< Current sequence ended */
        BF_CAPTURE_CONTINUED,   /*!< Data added to current sequence */
        BF_CAPTURE_CHANGED,     /*!< Sequence parameters changed */
        BF_CAPTURE_NO_DATA,     /*!< No data received (timeout) */
        BF_CAPTURE_INTERRUPTED, /*!< Capture was interrupted */
        BF_CAPTURE_ERROR        /*!< An error occurred */
} BFpacketcapture_status;

/*! \p bfDiskReaderCreate creates a packet reader from disk files
 *
 *  \param obj               Pointer to receive the capture handle
 *  \param format            Packet format string (e.g., "vdif", "tbn", "drx")
 *  \param fd                Open file descriptor to read from
 *  \param ring              Ring buffer to write data to
 *  \param nsrc              Number of sources in the data
 *  \param src0              First source index
 *  \param buffer_ntime      Number of time samples to buffer
 *  \param slot_ntime        Number of time samples per slot
 *  \param sequence_callback Callback for sequence events
 *  \param core              CPU core affinity (-1 for none)
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfDiskReaderCreate(BFpacketcapture* obj,
                            const char*      format,
                            int              fd,
                            BFring           ring,
                            BFsize           nsrc,
                            BFsize           src0,
                            BFsize           buffer_ntime,
                            BFsize           slot_ntime,
                            BFpacketcapture_callback sequence_callback,
                            int              core);
/*! \p bfUdpCaptureCreate creates a UDP packet capture object
 *
 *  \param obj               Pointer to receive the capture handle
 *  \param format            Packet format string
 *  \param fd                Bound UDP socket file descriptor
 *  \param ring              Ring buffer to write data to
 *  \param nsrc              Number of sources expected
 *  \param src0              First source index
 *  \param max_payload_size  Maximum UDP payload size in bytes
 *  \param buffer_ntime      Number of time samples to buffer
 *  \param slot_ntime        Number of time samples per slot
 *  \param sequence_callback Callback for sequence events
 *  \param core              CPU core affinity (-1 for none)
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpCaptureCreate(BFpacketcapture* obj,
                            const char*      format,
                            int              fd,
                            BFring           ring,
                            BFsize           nsrc,
                            BFsize           src0,
                            BFsize           max_payload_size,
                            BFsize           buffer_ntime,
                            BFsize           slot_ntime,
                            BFpacketcapture_callback sequence_callback,
                            int              core);
BFstatus bfUdpSnifferCreate(BFpacketcapture* obj,
                            const char*      format,
                            int              fd,
                            BFring           ring,
                            BFsize           nsrc,
                            BFsize           src0,
                            BFsize           max_payload_size,
                            BFsize           buffer_ntime,
                            BFsize           slot_ntime,
                            BFpacketcapture_callback sequence_callback,
                            int              core);
BFstatus bfUdpVerbsCaptureCreate(BFpacketcapture* obj,
                                 const char*      format,
                                 int              fd,
                                 BFring           ring,
                                 BFsize           nsrc,
                                 BFsize           src0,
                                 BFsize           max_payload_size,
                                 BFsize           buffer_ntime,
                                 BFsize           slot_ntime,
                                 BFpacketcapture_callback sequence_callback,
                                 int              core);
/*! \p bfPacketCaptureDestroy releases a capture object
 *
 *  \param obj The capture object to destroy
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketCaptureDestroy(BFpacketcapture obj);

/*! \p bfPacketCaptureRecv receives packets and writes to the ring
 *
 *  \param obj    The capture object
 *  \param result Pointer to receive the capture status
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketCaptureRecv(BFpacketcapture         obj,
                             BFpacketcapture_status* result);

/*! \p bfPacketCaptureFlush flushes any buffered data to the ring
 *
 *  \param obj The capture object
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketCaptureFlush(BFpacketcapture obj);

/*! \p bfPacketCaptureSeek seeks to a position in a disk reader
 *
 *  \param obj      The capture object (must be a disk reader)
 *  \param offset   Byte offset to seek
 *  \param whence   Seek origin (BF_WHENCE_SET, BF_WHENCE_CUR, BF_WHENCE_END)
 *  \param position Pointer to receive the new position
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketCaptureSeek(BFpacketcapture obj,
                             BFoffset        offset,
                             BFiowhence      whence,
                             BFoffset*       position);

/*! \p bfPacketCaptureTell returns the current file position
 *
 *  \param obj      The capture object (must be a disk reader)
 *  \param position Pointer to receive the current position
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketCaptureTell(BFpacketcapture obj,
                             BFoffset*       position);

/*! \p bfPacketCaptureEnd signals the end of capture
 *
 *  \param obj The capture object
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfPacketCaptureEnd(BFpacketcapture obj);
// TODO: bfPacketCaptureGetXX

/*! @} */

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_PACKET_CAPTURE_H_INCLUDE_GUARD_
