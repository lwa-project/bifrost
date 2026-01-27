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

/*! \file cuda.h
 *  \brief CUDA device and stream management functions
 *
 *  This module provides functions for managing CUDA devices and streams
 *  used by Bifrost GPU operations.
 */

#ifndef BF_CUDA_H_INCLUDE_GUARD_
#define BF_CUDA_H_INCLUDE_GUARD_

#include <bifrost/common.h>

#ifdef __cplusplus
extern "C" {
#endif

/*! \p bfStreamGet retrieves the current CUDA stream
 *
 *  \param stream Pointer to receive the CUDA stream handle
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfStreamGet(void*       stream);

/*! \p bfStreamSet sets the CUDA stream for subsequent operations
 *
 *  \param stream CUDA stream handle to use
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfStreamSet(void const* stream);

/*! \p bfStreamSynchronize waits for all operations on the current stream to complete
 *
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfStreamSynchronize();

/*! \p bfDeviceGet retrieves the current CUDA device index
 *
 *  \param device Pointer to receive the device index
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfDeviceGet(int* device);

/*! \p bfDeviceSet sets the active CUDA device by index
 *
 *  \param device Device index to activate
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfDeviceSet(int  device);

/*! \p bfDeviceSetById sets the active CUDA device by PCI bus ID
 *
 *  \param pci_bus_id PCI bus ID string (e.g., "0000:03:00.0")
 *  \return BF_STATUS_SUCCESS on success
 */
BFstatus bfDeviceSetById(const char* pci_bus_id);

// This must be called _before_ initializing any devices in the current process
/*! \p bfDevicesSetNoSpinCPU configures CUDA to not spin-wait on CPU
 *
 *  This reduces CPU usage when waiting for GPU operations but may
 *  slightly increase latency. Must be called before initializing
 *  any CUDA devices in the current process.
 *
 *  \return BF_STATUS_SUCCESS on success
 *  \note This must be called before any other CUDA operations
 */
BFstatus bfDevicesSetNoSpinCPU();

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BF_CUDA_H_INCLUDE_GUARD_
