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

/*! \file io.h
 *  \brief I/O method and seek constants
 *
 *  This module defines enumerations for I/O methods and file seek operations
 *  used by packet capture and other I/O functionality.
 */

#ifndef BF_IO_H_INCLUDE_GUARD_
#define BF_IO_H_INCLUDE_GUARD_

#include <unistd.h>

#ifdef __cplusplus
extern "C" {
#endif

/*! \brief I/O method types for packet capture */
typedef enum BFiomethod_ {
    BF_IO_GENERIC = 0,  /*!< Generic I/O (default) */
    BF_IO_DISK    = 1,  /*!< Disk file I/O */
    BF_IO_UDP     = 2,  /*!< UDP socket I/O */
    BF_IO_SNIFFER = 3,  /*!< Raw socket sniffer I/O */
    BF_IO_VERBS   = 4   /*!< Infiniband Verbs I/O */
} BFiomethod;

/*! \brief File seek origin constants */
typedef enum BFiowhence_ {
    BF_WHENCE_SET = SEEK_SET,  /*!< Seek from beginning of file */
    BF_WHENCE_CUR = SEEK_CUR,  /*!< Seek from current position */
    BF_WHENCE_END = SEEK_END   /*!< Seek from end of file */
} BFiowhence;

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_IO_H_INCLUDE_GUARD_
