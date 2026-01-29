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

/*! \file udp_socket.h
 *  \brief UDP socket operations
 *
 *  This module provides UDP socket functionality for network I/O,
 *  including binding, connecting, and packet sniffing modes.
 */

#ifndef BF_UDP_SOCKET_H_INCLUDE_GUARD_
#define BF_UDP_SOCKET_H_INCLUDE_GUARD_

#ifdef __cplusplus
extern "C" {
#endif

#include <bifrost/address.h>

typedef struct BFudpsocket_impl* BFudpsocket;

/*! \p bfUdpSocketCreate allocates a new UDP socket object
 *
 *  \param obj Pointer to receive the socket handle
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpSocketCreate(BFudpsocket* obj);
BFstatus bfUdpSocketDestroy(BFudpsocket obj);

/*! \p bfUdpSocketConnect connects the socket to a remote address
 *
 *  After connecting, send operations will target this address.
 *
 *  \param obj         The socket object
 *  \param remote_addr Remote address to connect to
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpSocketConnect(BFudpsocket obj, BFaddress remote_addr);

/*! \p bfUdpSocketBind binds the socket to a local address
 *
 *  \param obj        The socket object
 *  \param local_addr Local address to bind to
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpSocketBind(BFudpsocket obj, BFaddress local_addr);

/*! \p bfUdpSocketSniff enables packet capture mode on an interface
 *
 *  Opens a raw socket for capturing packets on the interface
 *  associated with the given address.
 *
 *  \param obj        The socket object
 *  \param local_addr Address identifying the interface to sniff
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpSocketSniff(BFudpsocket obj, BFaddress local_addr);

/*! \p bfUdpSocketShutdown disables further send/receive on the socket
 *
 *  \param obj The socket object
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpSocketShutdown(BFudpsocket obj);
BFstatus bfUdpSocketClose(BFudpsocket obj);
BFstatus bfUdpSocketSetTimeout(BFudpsocket obj, double secs);
BFstatus bfUdpSocketGetTimeout(BFudpsocket obj, double* secs);
BFstatus bfUdpSocketSetPromiscuous(BFudpsocket obj, int promisc);
BFstatus bfUdpSocketGetPromiscuous(BFudpsocket obj, int* promisc);

/*! \p bfUdpSocketGetMTU gets the interface maximum transmission unit
 *
 *  \param obj The socket object
 *  \param mtu Pointer to receive the MTU in bytes
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpSocketGetMTU(BFudpsocket obj, int* mtu);

/*! \p bfUdpSocketGetFD gets the underlying file descriptor
 *
 *  \param obj The socket object
 *  \param fd  Pointer to receive the file descriptor
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfUdpSocketGetFD(BFudpsocket obj, int* fd);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_UDP_SOCKET_H_INCLUDE_GUARD_
