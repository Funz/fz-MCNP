#!/usr/bin/env python3
"""
Basic test suite for fz-MCNP plugin.

These tests verify the plugin structure.
They test:
- Model file validity
- Variable parsing
- Input file compilation
- Calculator configuration
"""

import os
import json
import tempfile
import sys


def test_model_files():
    """Test that all model JSON files are valid and have required fields."""
    print("Testing model files...")
    
    models = [
        ".fz/models/MCNP.json"
    ]
    
    required_fields = ["id", "varprefix", "var_delim", "formulaprefix", "formula_delim",
                       "commentline", "output"]
    expected_outputs = ["mcnp_status", "mean_keff", "sigma_keff", "dkeff", "sigma_dkeff",
                        "tally", "tally_relerr"]
    
    for model_file in models:
        print(f"  Checking {model_file}...", end=" ")
        
        # Check file exists
        assert os.path.exists(model_file), f"File not found: {model_file}"
        
        # Load and validate JSON
        with open(model_file, 'r') as f:
            model = json.load(f)
        
        # Check required fields
        for field in required_fields:
            assert field in model, f"Missing field '{field}' in {model_file}"
        
        # Check output section has at least one variable
        assert len(model["output"]) > 0, f"No output variables in {model_file}"
        for name in expected_outputs:
            assert name in model["output"], f"Missing output variable '{name}'"
        # native Python extraction: no bash/awk needed to parse outputs (Windows)
        for name, cmd in model["output"].items():
            assert cmd.startswith("python://"), f"Output '{name}' is not a python:// expression"
        
        print("✓")
    
    print("  All model files valid!\n")


def test_calculator_files():
    """Test that calculator JSON files are valid."""
    print("Testing calculator configuration files...")

    calculators = [
        ".fz/calculators/localhost_MCNP.json"
    ]
    
    for calc_file in calculators:
        print(f"  Checking {calc_file}...", end=" ")
        
        # Check file exists
        assert os.path.exists(calc_file), f"File not found: {calc_file}"
        
        # Load and validate JSON
        with open(calc_file, 'r') as f:
            calc = json.load(f)
        
        # Check required fields
        assert "uri" in calc, f"Missing 'uri' field in {calc_file}"
        assert "models" in calc, f"Missing 'models' field in {calc_file}"
        
        print("✓")
    
    print("  All calculator files valid!\n")


def test_calculator_scripts():
    """Test that calculator shell scripts exist and are executable."""
    print("Testing calculator shell scripts...")
    
    scripts = [
        ".fz/calculators/MCNP.sh"
    ]
    
    for script_file in scripts:
        print(f"  Checking {script_file}...", end=" ")
        
        # Check file exists
        assert os.path.exists(script_file), f"File not found: {script_file}"
        
        # Check if executable
        assert os.access(script_file, os.X_OK), f"Script not executable: {script_file}"
        
        print("✓")
    
    print("  All calculator scripts valid!\n")


def test_example_files():
    """Test that example files exist."""
    print("Testing example files...")
    
    examples = [
        "examples/godiva.inp",
        "examples/example_godiva.py"
    ]
    
    for example_file in examples:
        print(f"  Checking {example_file}...", end=" ")
        assert os.path.exists(example_file), f"File not found: {example_file}"
        print("✓")
    
    print("  All example files present!\n")


def test_with_fz():
    """Test integration with fz framework (if available)."""
    print("Testing fz framework integration...")
    
    try:
        import fz
        print("  fz module found ✓")
        
        # Test parsing input file
        print("  Testing fz.fzi() on godiva.inp...", end=" ")
        variables = fz.fzi("examples/godiva.inp", "MCNP")
        assert "r" in variables, "Variable 'r' not found in parsed input"
        print("✓")
        
        # Test compiling input file
        print("  Testing fz.fzc() compilation...", end=" ")
        with tempfile.TemporaryDirectory() as tmpdir:
            fz.fzc(
                "examples/godiva.inp",
                {"r": 8.741},
                "MCNP",
                output_dir=tmpdir
            )
            
            # Check compiled file exists (it may be in a subdirectory)
            compiled_file = None
            for root, dirs, files in os.walk(tmpdir):
                if "godiva.inp" in files:
                    compiled_file = os.path.join(root, "godiva.inp")
                    break
            assert compiled_file is not None, "Compiled file not created"
            
            # Check variable was substituted
            with open(compiled_file, 'r') as f:
                content = f.read()
                assert "8.741" in content, "Variable r not substituted"
                assert "%(r)" not in content, "Variable marker %(r) still present"
                assert "@{" not in content, "Formula not evaluated"
                mass = 18.74 * 4.0 / 3.0 * 3.141592653589793 * 8.741 ** 3
                assert f"{mass:.0f}" in content, "Formula (sphere mass) not evaluated"
        print("✓")
        
        print("  fz integration tests passed!\n")
        
    except ImportError:
        print("  fz module not installed - skipping integration tests")
        print("  (Install with: pip install git+https://github.com/Funz/fz.git)\n")


def main():
    """Run all tests."""
    print("=" * 70)
    print("fz-MCNP Plugin Test Suite")
    print("=" * 70)
    print()
    
    # Change to repository root if needed
    if not os.path.exists(".fz"):
        if os.path.exists("../fz-MCNP/.fz"):
            os.chdir("../fz-MCNP")
        else:
            print("Error: Could not find .fz directory")
            print("Please run this script from the fz-MCNP repository root")
            return 1
    
    try:
        test_model_files()
        test_calculator_files()
        test_calculator_scripts()
        test_example_files()
        test_with_fz()
        
        print("=" * 70)
        print("All tests passed! ✓")
        print("=" * 70)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
