#!/usr/bin/env python3
"""
Example script for running MCNP parametric studies with fz.

This example demonstrates how to use the fz-mcnp plugin to run
a parametric study on the Godiva critical reactor, varying the
sphere radius to study criticality.
"""

import os
import sys

try:
    import fz
except ImportError:
    print("Error: fz framework not found.")
    print("Please install it from: https://github.com/Funz/fz")
    sys.exit(1)


def main():
    """Run a parametric study on the Godiva critical reactor."""
    
    # Check if MCNP_PATH is set
    if 'MCNP_PATH' not in os.environ:
        print("Warning: MCNP_PATH environment variable is not set.")
        print("Please set it to your MCNP installation directory:")
        print("  export MCNP_PATH=/path/to/your/MCNP6")
        print("\nFor demonstration purposes, setting a placeholder path...")
        os.environ['MCNP_PATH'] = '/Applications/MCNP6'
        print("(You will need to update this for actual calculations)\n")
    
    # Define the input file (in the same directory as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "godiva.inp")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Please run this script from the examples directory.")
        sys.exit(1)
    
    print("=" * 60)
    print("MCNP Parametric Study: Godiva Critical Reactor")
    print("=" * 60)
    print()
    
    # Define parameter values to study
    # Testing different sphere radii around the critical radius
    input_variables = {
        "r": [8.5, 8.741, 9.0]  # Sphere radius in cm
    }
    
    print("Parameters:")
    for var, values in input_variables.items():
        print(f"  {var}: {values}")
    print()
    
    print("Running calculations...")
    print("-" * 60)
    
    # Run the parametric study
    try:
        results = fz.fzr(
            input_path=input_file,
            input_variables=input_variables,
            model="MCNP",
            calculators="localhost_MCNP",
            results_dir="results"
        )
        
        print()
        print("=" * 60)
        print("Results:")
        print("=" * 60)
        print()
        print(results)
        print()
        
        # Summary statistics
        print("-" * 60)
        print(f"Total calculations: {len(results)}")
        successful = len(results[results['status'] == 'done'])
        print(f"Successful: {successful}")
        print(f"Failed: {len(results) - successful}")
        
        # Analyze results if successful
        if successful > 0:
            print()
            print("Critical Analysis:")
            print("-" * 60)
            for idx, row in results.iterrows():
                r = row['r']
                keff = row.get('mean_keff', 'N/A')
                sigma = row.get('sigma_keff', 'N/A')
                if keff != 'N/A' and keff is not None:
                    status = "supercritical" if keff > 1.0 else "subcritical" if keff < 1.0 else "critical"
                    print(f"  r={r:.3f} cm: k_eff = {keff:.4f} ± {sigma:.4f} ({status})")
                else:
                    print(f"  r={r:.3f} cm: Calculation failed or incomplete")
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nMake sure you have:")
        print("1. The fz framework installed")
        print("2. MCNP installed and MCNP_PATH set correctly")
        print("3. The .fz/models and .fz/calculators directories present")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during calculation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Study completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
