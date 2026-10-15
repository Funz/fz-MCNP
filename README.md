# fz-MCNP

[fz](https://github.com/Funz/fz) plugin for MCNP6 (Monte Carlo N-Particle transport code):
parametric criticality (`KCODE`) and fixed-source studies.

## Features

- Variable substitution and formulas in MCNP input files
- Extraction of the run status (with the first MCNP error message), keff and its standard
  deviation, `PERT` keff changes, and tally results from `MCTAL`
- Success decided from the MCNP output (`outp`), not from the executable exit code

### Input

- **File types**: any MCNP input; the input file is the first file named `*.inp`, `*.i`,
  `*.mcnp` or `*.mcn`, else the first file that is not an MCNP output (inputs without
  extension, like `godiva`, are accepted). Other files are passed along as resources.
- **Parameter syntax** (same as the Java Funz `plugin-MCNP`):
  - variables: `%(name)`, with optional default `%(name~8.74)` or range `%(name~[8.5,9.0])`
  - formulas: `@{expression}`, e.g. `@{round(18.74*4/3*3.141592653589793*%(r)**3)}`
  - fz context lines: `C @: <python code>` (capital `C` followed by a blank: `commentline` is
    `"C "`, and the match is case-sensitive; a lowercase `c @:` line is a plain MCNP comment)
- `%`, `@`, `{}` have no meaning in MCNP; `$` (MCNP comment) and `#` (cell complement) are
  deliberately not used.

Keep MCNP line rules in mind when substituting values: lines are limited to 128 columns, and
a formula result is written with full precision (e.g. `8.778051321790539`).

#### Example input (`examples/godiva.inp`)

```
Godiva-type critical reactor and kcode example
c 10000 neutrons per cycle, skip 30 cycles and run a total of 130 keff cycles
c sphere mass (g): @{round(18.74*4/3*3.141592653589793*%(r)**3)}
 1    1  -18.74  -1  imp:n=1   $ enriched uranium sphere (godiva)
 2    0           1  imp:n=0   $ all space outside the sphere

 1    so %(r)                 $ radius of the godiva sphere

 kcode 10000 1.0 30 130        $ kcode defines a criticality calculation
 ksrc  0 0 0                   $ initial keff spatial dist is point at origin
 m1    92235 -93.71  92238 -5.27  92234 -1.02  $ define u with weight fractions
```

ZAIDs without library suffix take the first table listed in `xsdir`, which depends on the
installation; give explicit suffixes (e.g. `92235.00c` with MCNP 6.3 / ENDF/B-VIII.0) for
production studies.

### Output

Files read: `outp` (MCNP is run with `o=outp`), `mctal` (written only with `PRDMP j j 1`),
and fz's `out.txt` (MCNP terminal output) when `outp` is missing.

| Variable | Content |
|---|---|
| `mcnp_status` | `NORMAL END`, `FATAL ERROR: <first fatal error>`, `BAD TROUBLE: <reason> (subroutine ...)`, `ABNORMAL END: run terminated because <reason>` (e.g. lost particles), `NO END BANNER` (interrupted run), `NO OUTPUT` |
| `mean_keff`, `sigma_keff` | final combined collision/absorption/track-length keff and its standard deviation (`KCODE` only) |
| `dkeff`, `sigma_dkeff` | keff change of each `PERTn` card (track-length estimator) and its standard deviation, flattened by fz into `dkeff_1`, `dkeff_2`, ... (absent without `PERT`) |
| `tally`, `tally_relerr` | for each tally of `mctal`, the last value of its `vals` block (the total bin when the tally has one) and its relative error, flattened into `tally_4`, `tally_relerr_4`, ... (absent without `mctal`) |

Example (real MCNP 6.1 output, `tests/fixtures/mcnp6.1/ok_godiva/outp`):

```
 | the final estimated combined collision/absorption/track-length keff = 1.00248 with an estimated standard deviation of 0.00062   |
```

gives `mean_keff` = 1.00248, `sigma_keff` = 0.00062. For a fixed-source run, `mean_keff`
and `sigma_keff` are empty (fz reports them in `_output_error`).

The `PERT` table and `MCTAL` formats are taken from the MCNP 6.3 documentation, not yet from
real runs: see [tests/mcnp_probe](tests/mcnp_probe/README.md).

### What `NORMAL END` does not tell

`mcnp_status` = `NORMAL END` with a keff and a small σ does not prove that the fission source
converged. According to the MCNP synthetic notice (skill v0.2): with loosely coupled units and
`KSRC` points in one unit only, MCNP 6.3 returned k = 0.928 instead of 0.993 while the entropy
check passed; a `KSRC` point in a non-fissile cell of non-zero importance is not rejected. In a
parametric study, check that `KSRC` points (or the `SDEF` volume) lie inside **every** fissile unit
for **all** sampled values of the variables (e.g. points written with formulas of the geometric
variables), give `HSRC` over the whole fissile region, and look at print table 126 (activity in
each cell) of a few cases.

## Installation

1. Install fz: `pip install git+https://github.com/Funz/fz.git`
2. Install the plugin:
   ```python
   import fz
   fz.install("MCNP")
   ```
3. Make MCNP available to the calculator script (`.fz/calculators/MCNP.sh`):

| Variable | Default | Role |
|---|---|---|
| `MCNP_CMD` | `mcnp6` on `PATH`, else `$MCNP_PATH/MCNP_CODE/bin/mcnp6`, else `$MCNP_PATH/bin/mcnp6` | MCNP executable |
| `MCNP_PATH` | none | installation directory (layout of the Java plugin: `MCNP_CODE/`, `MCNP_DATA/`) |
| `DATAPATH` | kept if set, else `$MCNP_PATH/MCNP_DATA` if it exists | directory holding `xsdir` |
| `MCNP_TASKS` | none | number of threads (`tasks N`) |
| `MCNP_OPTS` | none | extra command-line options, appended as given |

The script runs `mcnp6 i=<input> o=outp [tasks N] [MCNP_OPTS]` in the case directory,
removes a previous `outp`/`mctal` first (MCNP would otherwise write `outq`/`mctam`), and
sets `ulimit -s unlimited` when allowed. Exit codes: 0 normal end, 1 no input file,
2 usage, 4 executable not found, 5 no `outp`, 6 abnormal end (message on stderr),
7 `outp` without end banner. With `MCNP_OPTS=fatal` (transport despite fatal errors) the
case is still reported as failed.

## Usage

```python
import fz

results = fz.fzr(
    "examples/godiva.inp",
    {"r": [8.5, 8.7407, 9.0]},       # sphere radius (cm)
    "MCNP",
    calculators="localhost_MCNP",    # optional: found automatically
    results_dir="results",
)
print(results[["r", "status", "mcnp_status", "mean_keff", "sigma_keff"]])
```

Same with the CLI:

```bash
fzr --input_path examples/godiva.inp --model MCNP \
    --input_variables '{"r": [8.5, 8.7407, 9.0]}' --results_dir results --format json
```

Other entry points: `fz.fzi("examples/godiva.inp", "MCNP")` (variables),
`fz.fzc(..., output_dir="compiled")` (compiled inputs), `fz.fzo("results/*", "MCNP")`
(re-parse outputs), [examples/example_godiva.py](examples/example_godiva.py) and
[example_usage.ipynb](example_usage.ipynb).

Remote execution: give an `ssh://` or `slurm://` calculator running
`bash .fz/calculators/MCNP.sh` on a host where MCNP is installed (see the
[fz calculators documentation](https://github.com/Funz/fz/blob/main/doc/calculators.md));
results can be reused with a `cache://<previous results dir>` calculator placed first.

## Repository layout

```
fz-MCNP/
├── .fz/
│   ├── models/MCNP.json                # syntax and output extraction
│   └── calculators/
│       ├── MCNP.sh                     # runs mcnp6, checks outp
│       └── localhost_MCNP.json         # local calculator alias
├── examples/
│   ├── godiva.inp                      # parameterized Godiva input
│   └── example_godiva.py
├── tests/
│   ├── test_plugin.py                  # structure, fzi/fzc
│   ├── test_calculator.py              # MCNP.sh with a fake mcnp6
│   ├── test_outputs.py                 # output extraction on reference outputs
│   ├── test_fz_e2e.py                  # fzr end to end with a fake mcnp6
│   ├── fixtures/                       # real MCNP 6.1 output + synthetic outputs
│   └── mcnp_probe/                     # datasets to run with a real MCNP
└── example_usage.ipynb
```

## Tests

```bash
pip install pytest
pytest tests/                        # no MCNP needed
python tests/test_plugin.py          # structure checks only
```

With a real MCNP: `tests/mcnp_probe/run_probe.sh` (one dataset per hypothesis on the
plugin and on MCNP behaviour) and `tests/mcnp_probe/run_fz_e2e.py` (fzr on `godiva.inp`).

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `MCNP executable not found` (exit 4) | set `MCNP_CMD`, or put `mcnp6` on `PATH`, or set `MCNP_PATH` |
| `mcnp_status` = `BAD TROUBLE: data file xsdir... does not exist` | set `DATAPATH` to the directory holding `xsdir` |
| `FATAL ERROR: cross-section tables missing for zaid = ...` | ZAID/library not in your `xsdir` (natural elements have no ENDF/B-VII.1/VIII.0 table: use isotopes) |
| `FATAL ERROR: no m card for material ...` while the `M` card exists | a blank line inside the data block ends it: use `c` comment lines instead |
| `ABNORMAL END: run terminated because 10 particles got lost.` | geometry gap or overlap |
| `mean_keff` empty with `NORMAL END` | no `KCODE` (fixed source), or no active cycle |

## License

BSD 3-Clause, as the fz framework.

## Related links

- [fz](https://github.com/Funz/fz) — parametric computing framework
- [plugin-MCNP](https://github.com/Funz/plugin-MCNP) — legacy Java Funz plugin
- [MCNP](https://mcnp.lanl.gov/) — official MCNP site
