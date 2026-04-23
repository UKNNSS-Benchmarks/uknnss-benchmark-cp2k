#!/bin/bash

VER=2026.1

if [ ! -f v$VER.tar.gz ]; then
    wget https://github.com/cp2k/cp2k/archive/refs/tags/v$VER.tar.gz
fi
rm -rf cp2k-$VER
tar -xvf v$VER.tar.gz
cd cp2k-$VER

module load cmake scalapack fftw

cd tools/toolchain
CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:/opt/rocm-7.0.2/lib/cmake \
    ./install_cp2k_toolchain.sh \
        --with-cmake=system \
        --with-scalapack=system \
        --with-fftw=system \
        --enable-hip \
        --gpu-ver=Mi250 -j16 || exit

cd ../..
source tools/toolchain/install/setup

CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:/opt/rocm-7.0.2/lib/cmake \
    cmake -S . -B build \
        -DCP2K_USE_LIBXC=ON \
        -DCP2K_USE_LIBINT2=ON \
        -DCP2K_USE_SPGLIB=ON \
        -DCP2K_USE_ELPA=ON \
        -DCP2K_USE_SPLA=ON \
        -DCP2K_USE_SIRIUS=ON \
        -DCP2K_USE_COSMA=ON \
        -DCP2K_USE_MPI=ON \
        -DCP2K_USE_ACCEL=HIP \
        -DCP2K_SUPPORTED_HIP_ARCHITECTURES=Mi210  \
        -DCMAKE_HIP_ARCHITECTURES=gfx90a \
        -DCP2K_DBCSR_USE_CPU_ONLY=OFF \
        -DDBCSR_DIR=./tools/toolchain/install/dbcsr-2.9.0-hip/lib/cmake/dbcsr
