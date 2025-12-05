# fz-mcnp

FZ plugin for MCNP (Monte Carlo N-Particle Transport Code) calculations.

This plugin enables parametric studies with MCNP using the [fz framework](https://github.com/Funz/fz).

## Features

* **Input File Support**: Standard MCNP input files
* **Variable Syntax**: `%(...)` for parameters (e.g., `%(r)` for radius)
* **Formula Syntax**: `@{...}` for calculated expressions
* **Comment Character**: `C ` (note: includes trailing space)
* **Output Parsing**: Automatic extraction of `mean_keff` and `sigma_keff` from MCNP output

## Installation

### Prerequisites

1. **MCNP Installation**: You must have MCNP installed on your system
2. **Python 3.7+**: Required for the fz framework
3. **fz framework**: Install from [github.com/Funz/fz](https://github.com/Funz/fz)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Funz/fz-mcnp.git
   cd fz-mcnp
   ```

2. Set the MCNP_PATH environment variable:
   ```bash
   # On Linux/Mac:
   export MCNP_PATH="/path/to/your/MCNP6"
   
   # On Windows:
   set MCNP_PATH=C:\path\to\your\MCNP6
   ```

3. The plugin is ready to use! The `.fz` directory contains:
   - `.fz/models/MCNP.json` - Model definition
   - `.fz/calculators/MCNP.sh` - Calculation script
   - `.fz/calculators/localhost_MCNP.json` - Calculator configuration

## Usage

### Example: Godiva Critical Reactor Study

The repository includes example files in `examples/` demonstrating a parametric study of a Godiva-type critical reactor.

**Input file (`examples/godiva.inp`):**
```
Godiva-type critical reactor and kcode example
c skip 10 and run a total of 110 keff cycles with 1000 neutrons per cycle
 1    1  -18.74  -1  imp:n=1   $ enriched uranium sphere (godiva)
 2    0           1  imp:n=0   $ all space outside the sphere

 1    so %(r)                 $ radius of the godiva sphere

 kcode 1000 1.0 10 1010         $ kcode defines a criticality calculation
 ksrc  0 0 0                   $ initial keff spatial dist is point at origin
 m1    92235 -93.71  92238 -5.27  92234 -1.02  $ define u with weight fractions
```

**Python script to run parametric study (`examples/example_godiva.py`):**
```python
import fz
import os

# Set MCNP_PATH if not already set
os.environ['MCNP_PATH'] = '/Applications/MCNP6'  # Adjust for your installation

# Define parameter values
input_variables = {
    "r": [8.5, 8.741, 9.0]  # Three different sphere radii
}

# Run parametric study
results = fz.fzr(
    input_path="examples/godiva.inp",
    input_variables=input_variables,
    model="MCNP",
    calculators="localhost_MCNP",
    results_dir="results"
)

# Display results
print(results)
print(f"\nCompleted {len(results)} calculations")
```

**Expected output:**
```
     r  mean_keff  sigma_keff  status     calculator
0  8.5     0.9850      0.0012    done  localhost_MCNP
1  8.741   0.9995      0.0006    done  localhost_MCNP
2  9.0     1.0145      0.0008    done  localhost_MCNP

Completed 3 calculations
```

### Input File Syntax

#### Variables
Use `%(variable_name)` to define parameters:
```
 1    so %(radius)                $ sphere radius
 kcode %(neutrons) 1.0 10 %(cycles)  $ neutron count and cycles
```

#### Formulas
Use `@{expression}` for calculated values:
```
c Calculate volume from radius
c @{volume = 4.0/3.0 * 3.14159 * %(radius)**3}
c Volume: @{volume} cm^3
```

#### Comments
MCNP comments start with `C ` (capital C followed by space):
```
C This is a comment line in MCNP format
c This is also a valid comment (lowercase c)
```

### Output Files

MCNP produces several output files:
- `outp` - Main output file containing results
- `runtpe` - Binary run tape file
- `srctp` - Source tape file

The plugin automatically extracts:
- **mean_keff**: Final estimated combined k-effective value
- **sigma_keff**: Standard deviation of k-effective

## Advanced Usage

### Using with Remote Calculators

Run MCNP on a remote server via SSH:

```python
import fz

results = fz.fzr(
    "examples/godiva.inp",
    {"r": [8.5, 8.741, 9.0]},
    "MCNP",
    calculators="ssh://user@hpc.example.com/bash /path/to/fz-mcnp/.fz/calculators/MCNP.sh",
    results_dir="remote_results"
)
```

### Using Cache for Reusing Results

```python
import fz

# First run
results1 = fz.fzr(
    "examples/godiva.inp",
    {"r": [8.5, 8.741, 9.0]},
    "MCNP",
    calculators="localhost_MCNP",
    results_dir="run1"
)

# Second run with additional values - reuses previous results
results2 = fz.fzr(
    "examples/godiva.inp",
    {"r": [8.5, 8.741, 9.0, 9.5, 10.0]},  # Added 9.5 and 10.0
    "MCNP",
    calculators=[
        "cache://run1",          # Check cache first
        "localhost_MCNP"         # Only run new cases
    ],
    results_dir="run2"
)
```

### Parallel Execution

Run multiple MCNP calculations in parallel:

```python
import fz

# Use multiple calculator instances for parallel execution
results = fz.fzr(
    "examples/godiva.inp",
    {"r": list(range(8, 11, 0.1))},  # Many parameter values
    "MCNP",
    calculators=["localhost_MCNP"] * 4,  # 4 parallel workers
    results_dir="parallel_results"
)
```

## Model Configuration

The MCNP model is defined in `.fz/models/MCNP.json`:

```json
{
    "id": "MCNP",
    "varprefix": "%",
    "formulaprefix": "@",
    "delim": "()",
    "commentline": "C ",
    "output": {
        "mean_keff": "grep 'the final estimated combined' outp | head -n 1 | awk '{match($0, /keff = ([0-9.]+)/, arr); print arr[1]}'",
        "sigma_keff": "grep 'the final estimated combined' outp | head -n 1 | awk '{match($0, /standard deviation of ([0-9.]+)/, arr); print arr[1]}'"
    }
}
```

You can customize this configuration to extract additional outputs from MCNP.

## Troubleshooting

### MCNP not found
**Error**: `MCNP executable not found`

**Solution**: Set the `MCNP_PATH` environment variable:
```bash
export MCNP_PATH="/path/to/your/MCNP6"
```

### Stack size issues
**Error**: MCNP crashes with stack-related errors

**Solution**: The script automatically sets `ulimit -s unlimited`, but if issues persist, manually set it before running:
```bash
ulimit -s unlimited
python your_script.py
```

### Output parsing fails
**Error**: `mean_keff` or `sigma_keff` returns None

**Solution**: Check that your MCNP input file contains a `kcode` card for criticality calculations. The output parser looks for lines containing "the final estimated combined".

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes with actual MCNP calculations
4. Submit a pull request

## License

This plugin follows the same license as the fz framework (BSD 3-Clause).

## Related Links

- [fz framework](https://github.com/Funz/fz) - Main parametric computing framework
- [Original MCNP plugin](https://github.com/Funz/plugin-MCNP) - Legacy plugin for reference
- [MCNP Documentation](https://mcnp.lanl.gov/) - Official MCNP documentation

## Citation

If you use this plugin in your research, please cite:

```bibtex
@software{fz_mcnp,
  title = {fz-mcnp: MCNP Plugin for FZ Parametric Computing Framework},
  year = {2025},
  url = {https://github.com/Funz/fz-mcnp}
}
```