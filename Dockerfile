ARG CUDA_VERSION=12.6.3
ARG UBUNTU_VERSION=22.04
ARG CUDA_IMAGE=nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}
ARG BASE_IMAGE=ubuntu:${UBUNTU_VERSION}
ARG DEBIAN_FRONTEND=noninteractive

# Accept GPU architectures as a build argument with an empty default
ARG GPU_ARCHS=""
ARG BUILD_TYPE=gpu
ARG BUILD_DOCS=0

# Select base image based on BUILD_TYPE
FROM ${CUDA_IMAGE} as base-gpu
FROM ${BASE_IMAGE} as base-cpu

# The actual base will be selected at build time
FROM base-${BUILD_TYPE} as base

MAINTAINER Ben Barsdell <benbarsdell@gmail.com>

# Get common dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        pkg-config \
        software-properties-common \
        python3 \
        python3-dev \
        python3-pip \
        python-is-python3 \
        python3-venv \
        pylint \
        universal-ctags \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up a Python virtual environment to avoid externally-managed-environment
# errors on newer versions of Python
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Documentation dependencies (only installed if BUILD_DOCS=1)
RUN if [ "${BUILD_DOCS}" = "1" ]; then \
        apt-get update && apt-get install -y --no-install-recommends \
            doxygen \
            && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*; \
    fi

# Install common Python packages
RUN pip --no-cache-dir install \
        setuptools \
        numpy \
        scipy \
        jupyterlab \
        jupyter_client \
        nbformat \
        nbconvert \
        matplotlib \
        contextlib2 \
        simplejson \
        pint \
        ctypesgen==1.0.2 \
        graphviz

# Documentation Python packages (only installed if BUILD_DOCS=1)
RUN if [ "${BUILD_DOCS}" = "1" ]; then \
        pip --no-cache-dir install \
            sphinx \
            breathe; \
    fi

# Install GPU-specific packages if CUDA is available
# This command only runs if CUDA is installed in the image
RUN if command -v nvcc > /dev/null; then \
        pip --no-cache-dir install \
            cupy-cuda12x \
            pycuda \
            numba; \
    fi

ENV TERM xterm

# IPython
EXPOSE 8888

# Builder stage
FROM base as builder

# Copy source code
WORKDIR /bifrost
COPY . .

# Build the library
RUN make clean && \
    if command -v nvcc > /dev/null; then \
        ALL_GPU_ARCHS=$(nvcc -h | grep -Po "'compute_[0-9]{2,3}" | cut -d_ -f2 | sort | uniq | paste -s -d ' ') && \
        if [ -z "$GPU_ARCHS" ]; then \
            echo "No GPU_ARCHS provided, building all available..." && \
            GPU_ARCHS=$ALL_GPU_ARCHS; \
        fi && \
        echo "Building for GPU archs $GPU_ARCHS" && \
        ./configure --with-gpu-archs="$GPU_ARCHS" --with-shared-mem=49152; \
    else \
        echo "Building CPU-only version" && \
        ./configure --disable-cuda; \
    fi && \
    make -j && \
    if [ "${BUILD_DOCS}" = "1" ]; then \
        make doc; \
    fi && \
    make install

ENV LD_LIBRARY_PATH /usr/local/lib:${LD_LIBRARY_PATH}

# Set working directory for user when container starts
WORKDIR /workspace
CMD ["/bin/bash"]
