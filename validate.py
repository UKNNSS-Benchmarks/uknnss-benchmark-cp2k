#!/usr/bin/env python3

import sys

def usage():
    print("validate.py: test output correctness for the UK-NNSS CP2K benchmark.")
    print("Usage: validate.py <output_file>")
#usage

def parse_output( fname ):

    natom = None
    energy  = None
    time = None

    f = open( fname, 'r' )
    for l in f:

        if("Atoms:" in l ):
            s = l.split()
            if( s[1]=="Atoms:"):
                natom = int(s[2])

        if("ENERGY|" in l ):
            s = l.split()
            if( s[0]=="ENERGY|"):
                energy = float(s[8])


        if("CP2K     " in l ):
            s = l.split()
            if( s[0]=="CP2K"):
                time = float(s[6])
            
    #end while
    f.close()
            
    if( not natom ):
        print("Error: could not find number of atoms in {:}".format( fname ) )
        print("       should have found \"    - Atoms:  \"" )
        exit(1)

    if( not energy ):
        print("Error: could not find final energy in {:}".format( fname ) )
        print("       should have found \"ENERGY| Total FORCE_EVAL ( QS ) energy [hartree] \"" )
        exit(1)

    if( not time ):
        print("Error: could not find run time  in {:}".format( fname ) )
        print("       should have found it after line:\"" )
        print("       SUBROUTINE                       CALLS  ASD         SELF TIME        TOTAL TIME" )
        exit(1)

    return natom, energy, time
#parse_output

def check_result( natom, energy ):

    natom_ref_l = [96, 768, 2592, 6144, 12000, 20736]
    nrep_ref_l = {
        96: 1,
        768: 2,
        2592: 3,
        6144: 4,
        12000: 5,
        20736: 6
    }
    e_ref_l = {
        96: -118874.30605090,
        768: -118874.30605090,
        2592: -118874.30605090,
        6144: -118874.30605090,
        12000: -118874.30605090,
        20736: -118874.30605090
    }

    print(f"         Number of atoms: {natom} ")

    if (natom not in natom_ref_l):
        print(f"    Measured: {energy:.8f} hartree")
        print("     Not reference case - skipping energy comparison")
        status_passed = False
    else:
        print(f"  Reference case # atoms: {natom_ref} (NREP {nrep_ref_l[natom]})\n")
        e_tol = 0.000001
        e_ref = e_ref_l[natom]
        e_err = abs( ( energy - e_ref ) / e_ref )
        status_passed = ( e_err < e_tol )
        print(f"    Measured: {energy:.8f} hartree")
        print(f"   Reference: {e_ref:.8f} hartree")
        print(f"  Difference: {e_err:.8f} hartree")
        print(f"   Tolerance: {e_tol:.8f} hartree")
    
    print("  Validation:", ("PASSED" if status_passed else "FAILED") )

    return status_passed
#check_result

def main():

    if( len(sys.argv) != 2 ):
        usage()
        exit(1)

    if( sys.argv[1] == "--help" ):
        usage()
        exit(0)
            
    fname = sys.argv[1]

    print("\n# CP2K H2O-dft-ls benchmark validation\n")

    natom, energy, time = parse_output(fname)

    status_passed = check_result(natom, energy)

    print(f"\n  BenchmarkTime: {time:.1f} s\n")
        
#main

main()
