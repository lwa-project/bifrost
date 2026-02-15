/*
 * Copyright (c) 2025, The Bifrost Authors. All rights reserved.
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

#pragma once

#include "base.hpp"

struct __attribute__((packed)) tbx_hdr_type {
    uint32_t sync_word;
    uint32_t frame_count_word;
    uint32_t seconds_count;
    uint32_t first_chan;
    uint16_t nstand;
    uint16_t nchan;
    uint64_t time_tag;
};

template<int16_t NSTAND>
class TBXHeaderFiller : virtual public PacketHeaderFiller {
    int16_t            _nstand = NSTAND;
public:
    inline int get_size() { return sizeof(tbx_hdr_type); }
    inline void operator()(const PacketDesc* hdr_base,
                           BFoffset          framecount,
                           char*             hdr) {
        tbx_hdr_type* header = reinterpret_cast<tbx_hdr_type*>(hdr);
        memset(header, 0, sizeof(tbx_hdr_type));
        
        header->sync_word        = 0x5CDEC0DE;
        // Bits 9-32 are the frame count; bits 1-8 are the TBX packet flag
        header->frame_count_word = htobe32((framecount & 0xFFFFFF) \
                                           | ((uint32_t) 0x08 << 24));
        header->first_chan       = htobe32(hdr_base->src);
        header->nstand           = htons(_nstand);
        header->nchan            = htons(hdr_base->nchan);
        header->time_tag         = htobe64(hdr_base->seq);
    }
};
