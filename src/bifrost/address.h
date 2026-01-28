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

/*! \file address.h
 *  \brief Network address creation and manipulation functions
 *
 *  This module provides functionality for creating and querying network
 *  addresses for UDP I/O operations.
 */

#ifndef BF_ADDRESS_H_INCLUDE_GUARD_
#define BF_ADDRESS_H_INCLUDE_GUARD_

#include <bifrost/common.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct sockaddr* BFaddress;

/*! \p bfAddressCreate creates a new network address object
 *
 *  \param addr         Pointer to receive the created address handle
 *  \param addr_string  IP address string (e.g., "192.168.1.1")
 *  \param port         UDP port number
 *  \param family       Address family (AF_INET or AF_UNSPEC for auto-detect)
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfAddressCreate(BFaddress*  addr,
                         const char* addr_string,
                         int         port,
                         unsigned    family);
/*! \p bfAddressDestroy releases an address object
 *
 *  \param addr The address to destroy
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfAddressDestroy(BFaddress addr);

/*! \p bfAddressGetFamily retrieves the address family
 *
 *  \param addr   The address object
 *  \param family Pointer to receive the address family
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfAddressGetFamily(BFaddress addr, unsigned* family);

/*! \p bfAddressGetPort retrieves the port number
 *
 *  \param addr The address object
 *  \param port Pointer to receive the port number
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfAddressGetPort(BFaddress addr, int* port);

/*! \p bfAddressIsMulticast checks if the address is a multicast address
 *
 *  \param addr      The address object
 *  \param multicast Pointer to receive 1 if multicast, 0 otherwise
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfAddressIsMulticast(BFaddress addr, int* multicast);

/*! \p bfAddressGetMTU retrieves the Maximum Transmission Unit for the address
 *
 *  \param addr The address object
 *  \param mtu  Pointer to receive the MTU in bytes
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfAddressGetMTU(BFaddress addr, int* mtu);

/*! \p bfAddressGetString converts the address to a string representation
 *
 *  \param addr    The address object
 *  \param bufsize Size of the output buffer (128 bytes is always sufficient)
 *  \param buf     Buffer to receive the address string
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfAddressGetString(BFaddress addr,
                            BFsize    bufsize, // 128 should always be enough
                            char*     buf);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_ADDRESS_H_INCLUDE_GUARD_
