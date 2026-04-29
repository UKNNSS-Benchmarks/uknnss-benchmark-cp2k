# UK NNSS CP2K benchmark

This repository describes the CP2K benchmark for the UK NNSS procurement.

> [!IMPORTANT]
> Please do not contact the benchmark or code maintainers directly with any questions. All questions must be submitted via the procurement response mechanism.

## Benchmark Overview
CP2K is a quantum chemistry and solid state physics software package that
can perform atomistic simulations of solid state, liquid, molecular, periodic,
material, crystal, and biological systems. CP2K provides a general framework
for different modeling methods such as DFT using the mixed Gaussian and plane
waves approaches GPW and GAPW. Supported theory levels include DFTB, LDA, GGA,
MP2, RPA, semi-empirical methods (AM1, PM3, PM6, RM1, MNDO, …), and classical
force fields (AMBER, CHARMM, …). CP2K can do simulations of molecular dynamics,
metadynamics, Monte Carlo, Ehrenfest dynamics, vibrational analysis, core level
spectroscopy, energy minimization, and transition state optimization using NEB
or dimer method. CP2K is written in Fortran 2008

The specific benchmark used for this procurement is the H2O-DFT-LS benchmark available
in the main CP2K repository on Github. This is a large system that runs a single-point
energy calculation using linear scaling DFT.

CP2K stresses both the GPU and CPU simultaneously for this benchmark case.

## Software

Git repository: [CP2K](https://github.com/cp2k/cp2k)

> [!CAUTION]
> All results submitted should be based on the following repository commit:
>- CP2K repository: [release version 2026.1 (757bb76)](https://github.com/cp2k/cp2k/releases/tag/v2026.1)

## Building the benchmark

Compiling the code involves two main steps:

1. building the third-party dependencies

   ```
   cd cp2k-2026.1/tools/toolchain
   ./install_cp2k_toolchain.sh  -j16
   ```

   Additional flags can be supplied to target specific hardware and customise the use of system-installed libraries. For example,
   ```
   --enable-cuda --gpu-ver=H100 --enable-cray
   ```
   or
   ```
   --with-scalapack=system --enable-hip --gpu-ver=Mi250
   ```
   See the help message for full list of available flags.

2. building CP2K
   ```
   cd cp2k-2026.1
   source tools/toolchain/install/setup

   CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:/opt/rocm-7.0.2/lib/cmake  \
     cmake -S . -B build \
       -DCP2K_USE_LIBXC=ON -DCP2K_USE_LIBINT2=ON -DCP2K_USE_SPGLIB=ON \
       -DCP2K_USE_ELPA=ON -DCP2K_USE_SPLA=ON -DCP2K_USE_SIRIUS=ON \
       -DCP2K_USE_COSMA=ON -DCP2K_USE_MPI=ON -DCP2K_DBCSR_USE_CPU_ONLY=OFF \
       -DDBCSR_DIR=./tools/toolchain/install/dbcsr-2.9.0-hip/lib/cmake/dbcsr \
       -DCP2K_USE_ACCEL=HIP -DCP2K_SUPPORTED_HIP_ARCHITECTURES=Mi210 \
       -DCMAKE_HIP_ARCHITECTURES=gfx90a
   ```
   modifying the last three lines with appropriate architecture-specific flags.

Detailed instructions are provided with the software package.

### Example build scripts
Example build scripts are provided for:
- NVIDIA GH200 system ([IsambardAI](https://docs.isambard.ac.uk/specs/#system-specifications-isambard-ai-phase-2)): [build_cp2k_GH200-IsambardAI.sh](build_cp2k_GH200-IsambardAI.sh)
- AMD MI210 system: [build_cp2k_MI210.sh](build_cp2k_MI210.sh)

### Allowed modifications

Some users reported issues using the vanilla toolchain supplied versions of OpenBLAS with Scalapack due to linker error with multiply defined symbols. 
Benchmarkers are allowed to use their own system stack versions of these two components and to let the benchmark workagainst these libraries.


## Running the benchmark

Input files for the CP2K H2O-dft-ls benchmark 
are provided in the [benchmark](./benchmark) directory. The directory also
contains example Slurm batch submission scripts from running the benchmark
on the 
[IsambardAI system](https://docs.isambard.ac.uk/specs/#system-specifications-isambard-ai-phase-2).

Example output from the running the benchmark on IsambardAI using 32 nodes
(128 GH200 superchip) with NVIDIA MPS (8 MPI processes per GPU) is also provided
in the [benchmark](./benchmark)  directory.

The parameter "NREP" in the `H2O-dft-ls.inp` file sets the problem size and 
is varied to provide all the data required from submission. The
number of atoms in the model scales cubically with NREP.

> [!TIP]
> For best performance from key DBSCR routines a square number of MPI
processes may need to be used (e.g. 64, 256, 1024). This applies to setups where benchmarkers are free to pick the configuration of MPI ranks. 

<i>TODO</i>: A remark on CPU-only is missing.

### Benchmark execution

Make sure all the input files are in the working directory and use the
parallel launcher (e.g. `srun` or `mpirun`) to run CP2K specifying the
input and output files using the `-i [inputfile].inp` and `-o [outputfile.out]`
options respectively. 

| Problem setup | Filename                 |
| ------------- | -------------------------|
| NREP 1        | H2O-dft-ls.NREP1.inp     |
| NREP 2        | H2O-dft-ls.NREP2.inp     |
| NREP 3        | H2O-dft-ls.NREP3.inp     |
| NREP 4        | H2O-dft-ls.NREP4.inp     |
| NREP 5        | H2O-dft-ls.NREP5.inp     |

> [!TIP]
> You may need to use a wrapper script to enable proper process
to GPU binding or to launch any multi-process per GPU services. 

The full example Slurm batch script and MPS wrapper script from IsambardAI
are available in this repository:

- [IsambardAI Slurm batch script](./benchmark/submit_isambard_mps.slurm)
- [IsambardAI MPS launch wrapper script](./benchmark/isambard-mps-wrapper.sh)

## Results

### Correctness results

Correctness can be verified using the [validate.py](./validate.py) script,
which compares the total energy to the expected value on computed on 
IsambardAI (the unit of energy is "Hartree"). 

Note: different values of NREP in the input file will produce different
total energies for the full system.

For example:

```
> ./validate.py --help
| validate.py: test output correctness for the CP2K benchmark.
| Usage: validate.py <output_file>
|

> ./validate.py benchmark/sample_output_32nodes_isambard.log

# CP2K H2O-dft-ls benchmark validation

         Number of atoms: 20736 
  Reference case # atoms: 20736 (NREP 6)

    Measured: -118874.30605090 hartree
   Reference: -118874.30605090 hartree
  Difference: 0.00000000 hartree
   Tolerance: 0.00000100 hartree
  Validation: PASSED

  BenchmarkTime: 35.2 s

```

### Performance results

In addition to testing for correctness, `validate.py` will also print the BenchmarkTime,
which is the sole FoM for the benchmark.
The BenchmarkTime printed by `validate.py` corresponds to the
elapsed time reported in the CP2K output file.

To be a valid FoM, the following conditions must be met:

- CP2K must be compiled with the commits stated above
  and must meet any source code modification restrictions stated above
- The CP2K input files must not be modified from the versions
  available in this repository (other than setting "NREP" as required)


### Reference data

#### IsambardAI (GH200)
The sample data in the table below are measured BencharkTime from the IsambardAI GPU system.
IsambardAI's GPU nodes each have four NVIDIA GH200 superchips;
GPU jobs used 32 MPI processes per node, 8 MPI processes per GPU and 9 OpenMP CPU 
threads per MPI process. [NVIDIA MPS](https://docs.nvidia.com/deploy/mps/index.html)  
is used to support multiple MPI processes per node as this gives improved performance
over a single MPI process per GPU.

The upper rows of the table describe performance change as the problem size increases.
The lower two rows show the performance of the benchmark problem size (NREP 6) for
two different GPU counts.

| Size      | # Atoms | # GH200  | # MPI per GPU | # MPI | BenchmarkTime (s) |
| ----      | ------: | -------: | ------------: | ----: | ----------------: |
| NREP 1    |      96 |        1 |             8 |     8 |              2.3  |
| NREP 2    |     768 |        1 |             8 |     8 |              9.0  |
| NREP 3    |    2592 |        1 |             8 |     8 |             75.7  |
| NREP 4    |    6144 |        4 |             8 |    32 |             75.7  |
| NREP 5    |   12000 |        8 |             8 |    64 |            104.9  |
| NREP 6    |   20736 |       32 |             8 |   256 |             90.2  |
| NREP 6    |   20736 |      128 |             8 |  1024 |             42.5  |

#### Hunter (Mi300A)

| Size      | # Atoms | # Mi300A | # MPI per GPU | # MPI | BenchmarkTime (s) |
| ----      | ------: | -------: | ------------: | ----: | ----------------: |
| NREP 1    |      96 |        1 |             8 |     8 |              9.0  |
| NREP 2    |     768 |        1 |             8 |     8 |             25.2  |
| NREP 3    |    2592 |        1 |             8 |     8 |            172.0  |
| NREP 6    |   20736 |       16 |             8 |   128 |            381.7  |


## License

This benchmark description and any associated files are released under the
MIT license.

## Changelog

The following changes to this document have been made since initial release:

| <div style="width:90px">Date</div> | Change |
|-----------:|--------|
| 2026-04-29 | Updates to Hunter reference data |