#!/usr/bin/env python3
# Copyright (c) 2016-2023, The Bifrost Authors. All rights reserved.
# Copyright (c) 2016, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of The Bifrost Authors nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from setuptools import setup, Extension, find_packages
import os
import sys
import glob

# Parse version file to extract __version__ value
bifrost_version_file = 'bifrost/version/__init__.py'
try:
    with open(bifrost_version_file, 'r') as version_file:
        for line in version_file:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            if '__version__' in line:
                __version__ = line.split('=', 1)[1].strip()
                __version__ = ''.join([c for c in __version__
                                       if c.isalnum() or c in ".-_"])
except IOError:
    if 'clean' in sys.argv[1:]:
        sys.exit(0)
    print("*************************************************************************")
    print("Please run `configure` and `make` from the root of the source tree to")
    print("generate", bifrost_version_file)
    print("*************************************************************************")
    raise

# Build up a list of scripts to install
scripts = glob.glob(os.path.join('..', 'tools', '*.py'))

setup(name='bifrost',
      version=__version__,
      description='Pipeline processing framework',
      author='Ben Barsdell',
      author_email='benbarsdell@gmail.com',
      url='https://github.com/lwa-project/bifrost',
      packages=find_packages(),
      scripts=scripts,
      python_requires='>=3.6',
      install_requires=[
          "numpy>=1.8.1",
          "contextlib2>=0.4.0",
          "pint>=0.7.0",
          "graphviz>=0.5.0",
          "ctypesgen==1.0.2",
          "matplotlib"
      ],
      ext_package='bifrost',
      ext_modules = [])
