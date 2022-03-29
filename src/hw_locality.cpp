/*
 * Copyright (c) 2019, The Bifrost Authors. All rights reserved.
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

#include "hw_locality.hpp"
#include  <stdexcept>

#if BF_HWLOC_ENABLED
int HardwareLocality::bind_memory_to_core(int core) {
    int core_depth = hwloc_get_type_or_below_depth(_topo, HWLOC_OBJ_CORE);
    int ncore      = hwloc_get_nbobjs_by_depth(_topo, core_depth);
    int ret = 0;
    if( 0 <= core && core < ncore ) {
        hwloc_obj_t    obj    = hwloc_get_obj_by_depth(_topo, core_depth, core);
#if HWLOC_API_VERSION >= 0x00020000
        hwloc_cpuset_t cpuset = hwloc_bitmap_dup(obj->cpuset);
        if( !hwloc_bitmap_intersects(cpuset, hwloc_topology_get_allowed_cpuset(_topo)) ) {
          throw std::runtime_error("requested core is not in the list of allowed cores");
        }
#else
        hwloc_cpuset_t cpuset = hwloc_bitmap_dup(obj->allowed_cpuset);
#endif
        hwloc_bitmap_singlify(cpuset); // Avoid hyper-threads
        hwloc_membind_policy_t policy = HWLOC_MEMBIND_BIND;
        hwloc_membind_flags_t  flags  = HWLOC_MEMBIND_THREAD;
        ret = hwloc_set_membind(_topo, cpuset, policy, flags);
        hwloc_bitmap_free(cpuset);
    }
    return ret;
}
#endif // BF_HWLOC_ENABLED
