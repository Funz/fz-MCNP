#!/usr/bin/env python3
"""
Parametric MCNP study with fz: keff of a Godiva sphere versus its radius.

Requirements: fz, MCNP (mcnp6 on PATH, or MCNP_CMD / MCNP_PATH set) and its
cross-section data (DATAPATH, or MCNP_PATH/MCNP_DATA). See README.md.

Run from anywhere: python3 examples/example_godiva.py
"""

import math
import os
import sys
from pathlib import Path

try:
    import fz
except ImportError:
    sys.exit("fz not found: pip install git+https://github.com/Funz/fz.git")

ROOT = Path(__file__).resolve().parents[1]


def main():
    # fz looks for .fz/models and .fz/calculators in the current directory (or ~/.fz)
    os.chdir(ROOT)

    results = fz.fzr(
        "examples/godiva.inp",
        {"r": [8.5, 8.7407, 9.0]},   # sphere radius (cm); Godiva critical radius ~ 8.74 cm
        "MCNP",
        calculators="localhost_MCNP",
        results_dir="results",
    )

    print(results[["r", "status", "mcnp_status", "mean_keff", "sigma_keff"]].to_string())

    for _, row in results.iterrows():
        try:
            keff, sigma = float(row["mean_keff"]), float(row["sigma_keff"])
        except (TypeError, ValueError):
            keff = sigma = math.nan
        if math.isnan(keff):
            print(f"r = {row['r']} cm: no keff ({row['mcnp_status']})")
        else:
            print(f"r = {row['r']} cm: keff = {keff:.5f} +/- {sigma:.5f}")

    return 0 if (results["status"] == "done").all() else 1


if __name__ == "__main__":
    sys.exit(main())
