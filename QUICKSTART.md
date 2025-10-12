# Quick Start Guide

Get started with fz-mcnp in 5 minutes!

## Prerequisites

1. **MCNP6** installed on your system
2. **Python 3.7+** installed
3. **fz framework** installed

## Step 1: Install fz Framework

```bash
git clone https://github.com/Funz/fz.git
cd fz
pip install -e .
```

## Step 2: Clone fz-mcnp

```bash
cd ..
git clone https://github.com/Funz/fz-mcnp.git
cd fz-mcnp
```

## Step 3: Set MCNP Path

```bash
# Linux/Mac:
export MCNP_PATH="/path/to/your/MCNP6"

# Windows (PowerShell):
$env:MCNP_PATH="C:\path\to\your\MCNP6"

# Windows (Command Prompt):
set MCNP_PATH=C:\path\to\your\MCNP6
```

**Common MCNP paths:**
- Mac: `/Applications/MCNP6`
- Linux: `/opt/MCNP6` or `/usr/local/MCNP6`
- Windows: `C:\MCNP\MCNP6`

## Step 4: Test the Installation

Run the example script:

```bash
python example_godiva.py
```

You should see output similar to:
```
============================================================
MCNP Parametric Study: Godiva Critical Reactor
============================================================

Parameters:
  r: [8.5, 8.741, 9.0]

Running calculations...
------------------------------------------------------------
[... calculation progress ...]

============================================================
Results:
============================================================

     r  mean_keff  sigma_keff  status     calculator
0  8.5     0.9850      0.0012    done  Localhost_MCNP
1  8.741   0.9995      0.0006    done  Localhost_MCNP
2  9.0     1.0145      0.0008    done  Localhost_MCNP

------------------------------------------------------------
Total calculations: 3
Successful: 3
Failed: 0

Critical Analysis:
------------------------------------------------------------
  r=8.500 cm: k_eff = 0.9850 ± 0.0012 (subcritical)
  r=8.741 cm: k_eff = 0.9995 ± 0.0006 (critical)
  r=9.000 cm: k_eff = 1.0145 ± 0.0008 (supercritical)

============================================================
Study completed successfully!
============================================================
```

## Step 5: Create Your Own Study

Create a new Python file `my_study.py`:

```python
import fz
import os

# Set MCNP path
os.environ['MCNP_PATH'] = '/path/to/your/MCNP6'

# Run your parametric study
results = fz.fzr(
    input_path="godiva.inp",      # Your MCNP input file
    input_variables={
        "r": [8.0, 8.5, 9.0, 9.5]  # Parameter values to study
    },
    model="MCNP",                  # Use MCNP model
    calculators="Localhost_MCNP",  # Use local calculator
    results_dir="my_results"       # Where to store results
)

# Analyze results
print(results)

# Access specific values
for idx, row in results.iterrows():
    print(f"r={row['r']}: k_eff = {row['mean_keff']:.4f} ± {row['sigma_keff']:.4f}")
```

Run it:
```bash
python my_study.py
```

## Common Issues

### Issue: "MCNP executable not found"

**Solution:** Check your MCNP_PATH is correct:
```bash
echo $MCNP_PATH  # Should show your MCNP directory
ls $MCNP_PATH/MCNP_CODE/bin/mcnp6  # Should exist
```

### Issue: "ModuleNotFoundError: No module named 'fz'"

**Solution:** Install the fz framework:
```bash
pip install -e /path/to/fz
```

### Issue: "Permission denied" when running MCNP

**Solution:** Make sure the script is executable:
```bash
chmod +x .fz/calculators/MCNP.sh
```

## Next Steps

1. **Modify the input file**: Edit `godiva.inp` to change the MCNP model
2. **Add more parameters**: Use `%(param)` syntax in your input file
3. **Run in parallel**: Use multiple calculators for faster execution
4. **Use remote HPC**: Set up SSH calculator for cluster execution
5. **Explore caching**: Reuse previous results to save computation time

## Example: Multi-Parameter Study

```python
import fz

# Study multiple parameters
results = fz.fzr(
    "godiva.inp",
    {
        "r": [8.5, 8.741, 9.0],           # Sphere radius
        "neutrons": [1000, 5000, 10000],  # Neutrons per cycle
        "cycles": [110, 510, 1010]        # Total cycles
    },
    "MCNP",
    calculators="Localhost_MCNP",
    results_dir="multi_param_study"
)

# This will run 3 × 3 × 3 = 27 calculations
print(f"Completed {len(results)} calculations")
```

## Need Help?

- Read the full [README.md](README.md)
- Check the [MIGRATION.md](MIGRATION.md) for details on porting from old plugin
- Visit the [fz framework documentation](https://github.com/Funz/fz)
- Open an issue on [GitHub](https://github.com/Funz/fz-mcnp/issues)

## Tips

- **Start small**: Test with a few parameter values first
- **Use caching**: Avoid re-running expensive calculations
- **Monitor resources**: MCNP can be memory-intensive
- **Check logs**: Look in results directories for detailed execution logs
- **Validate results**: Always verify MCNP completed successfully

Happy computing! 🚀
