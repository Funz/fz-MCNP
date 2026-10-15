#!/usr/bin/env python3
"""End-to-end test of the plugin through fz with a real MCNP.

Run from the repository root:
    MCNP_CMD=/path/to/mcnp6 DATAPATH=/path/to/data python3 tests/mcnp_probe/run_fz_e2e.py

Runs examples/godiva.inp (radius 8.5 / 8.7407 / 9.0) with the localhost_MCNP
calculator (.fz/calculators/MCNP.sh, which reads MCNP_CMD, MCNP_PATH,
DATAPATH, MCNP_TASKS and MCNP_OPTS from the environment).

Results: tests/mcnp_probe/results-fz-e2e/ (case directories + results.csv/.txt)
"""

import os
import shutil
from pathlib import Path

import fz

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tests" / "mcnp_probe" / "results-fz-e2e"

if __name__ == "__main__":
    os.chdir(ROOT)
    if OUT.exists():
        shutil.rmtree(OUT)
    results = fz.fzr(
        "examples/godiva.inp",
        {"r": [8.5, 8.7407, 9.0]},
        "MCNP",
        calculators="localhost_MCNP",
        results_dir=str(OUT),
    )
    results.to_csv(OUT / "results.csv", index=False)
    (OUT / "results.txt").write_text(results.T.to_string())
    cols = [c for c in ("r", "status", "mcnp_status", "mean_keff", "sigma_keff", "error")
            if c in results.columns]
    print(results[cols].to_string())
    print(f"Results: {OUT}")
