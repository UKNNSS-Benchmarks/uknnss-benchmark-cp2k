# Example build instructions: IsambardAI

[IsambardAI](https://docs.isambard.ac.uk/specs/#system-specifications-isambard-ai-phase-2)
is an HPE Cray EX system with NVIDIA GH200 and the HPE Cray Slingshot 11 interconnect.

**Download and unpack source code**

```
wget https://github.com/cp2k/cp2k/archive/refs/tags/v2026.1.tar.gz
tar -xvf v2026.1.tar.gz
```

**Build dependencies**

```
cd cp2k-2026.1/tools/toolchain

module load craype-network-ofi
module load PrgEnv-gnu 
module load gcc-native/13.2 
module load cray-mpich
module load cuda/12.6
module load craype-accel-nvidia90
module load craype-arm-grace
module load cray-python
module load cray-fftw

export CUDA_PATH=/opt/nvidia/hpc_sdk/Linux_aarch64/24.11/math_libs/12.6

./install_cp2k_toolchain.sh \
   --enable-cuda --gpu-ver=H100 \
   --enable-cray \
   -j16
```

**Build CP2K**

```
cd cp2k-2026.1

module load craype-network-ofi
module load PrgEnv-gnu 
module load gcc-native/13.2 
module load cray-mpich
module load cuda/12.6
module load craype-accel-nvidia90
module load craype-arm-grace
module load cray-python
module load cray-fftw

builddir=_build

mkdir $builddir
cd $builddir

source /projects/u6cb/software/CP2K/cp2k-2026.1/tools/toolchain/install/setup

export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_aarch64/24.11/math_libs/12.6/lib64:$LD_LIBRARY_PATH
export LDFLAGS="-L/opt/nvidia/hpc_sdk/Linux_aarch64/24.11/math_libs/12.6/lib64"
export CUDA_PATH=/opt/nvidia/hpc_sdk/Linux_aarch64/24.11/cuda/12.6
export CC=cc
export CXX=CC
export FC=ftn

cmake -S .. -B build \
    -DCP2K_USE_LIBXC=ON \
    -DCP2K_USE_LIBINT2=ON \
    -DCP2K_USE_SPGLIB=ON \
    -DCP2K_USE_ELPA=ON \
    -DCP2K_USE_SPLA=ON \
    -DCP2K_USE_SIRIUS=ON \
    -DCP2K_USE_COSMA=ON \
    -DCP2K_USE_MPI=ON \
    -DCP2K_USE_ACCEL=CUDA -DCP2K_WITH_GPU=H100 \
    -DCP2K_DBCSR_USE_CPU_ONLY=OFF \
    -DDBCSR_DIR=/projects/u6cb/software/CP2K/cp2k-2026.1/tools/toolchain/install/dbcsr-2.9.0-cuda/lib/cmake/dbcsr

cmake --build build -j 32 
```
