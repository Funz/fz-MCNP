#!/usr/bin/env python3
"""Synthese des resultats produits par run_probe.sh.

Usage : python3 summarize.py results-<label>-<date>/

Pour chaque cas : code retour, fichiers produits, version, banniere de fin,
erreurs, lignes keff, tableau PERT, debut de mctal, et le statut extrait par
le modele du plugin (.fz/models/MCNP.json) quand fz est installe. Les motifs
sont volontairement larges : le but est de consolider les formats reels.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

MARKERS = {
    "version": re.compile(r"Code Name & Version|^1mcnp\s+version", re.I),
    "end": re.compile(r"run terminated|mcrun\s+is done", re.I),
    "fatal": re.compile(r"fatal error", re.I),
    "bad_trouble": re.compile(r"bad trouble", re.I),
    "lost": re.compile(r"lost particle|particles got lost", re.I),
    "keff": re.compile(r"final estimated combined|final k\(col|no final keff", re.I),
    "warning": re.compile(r"^\s*warning\.", re.I),
}
MAX_HITS = 6
ROOT = Path(__file__).resolve().parents[2]


def scan(path):
    hits = {k: [] for k in MARKERS}
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return hits, []
    for i, line in enumerate(lines, 1):
        for key, rx in MARKERS.items():
            if rx.search(line) and len(hits[key]) < MAX_HITS:
                hits[key].append(f"{path.name}:{i}: {line.strip()[:150]}")
                if key == "bad_trouble" and i < len(lines):
                    hits[key].append(f"{path.name}:{i + 1}: {lines[i].strip()[:150]}")
    return hits, lines


def pert_table(lines):
    for i, line in enumerate(lines):
        if re.search(r"perturbation\s+k\(", line):
            return lines[max(0, i - 1):i + 8]
    return []


def model_outputs(case_dir):
    """Outputs of the plugin model on this case (None if fz is not importable)."""
    try:
        import fz
    except ImportError:
        return None
    model = json.loads((ROOT / ".fz" / "models" / "MCNP.json").read_text())
    try:
        row = fz.fzo(str(case_dir), model).iloc[0].to_dict()
    except Exception as e:  # report, do not stop the summary
        return {"error": repr(e)}
    return {k: v for k, v in row.items() if k not in ("path",) and not k.startswith("_")}


def main(results_dir):
    root = Path(results_dir)
    print((root / "environment.txt").read_text() if (root / "environment.txt").exists() else "")
    for case_dir in sorted(d for d in root.iterdir() if d.is_dir()):
        rd = lambda n: (case_dir / n).read_text().strip() if (case_dir / n).exists() else "?"
        print("=" * 100)
        print(f"{case_dir.name}   rc={rd('.exit_code')}   duree={rd('.duration_s')}s")
        print("  fichiers produits :")
        for line in rd(".files_after").splitlines():
            if not Path(line.split()[-1]).name.startswith("."):
                print(f"    {line}")
        for name in ("outp", "outq", "stdout.txt", "stderr.txt"):
            path = case_dir / name
            if not path.exists():
                continue
            hits, lines = scan(path)
            for key, found in hits.items():
                if found:
                    print(f"  [{name} / {key}]")
                    for h in found:
                        print(f"    {h}")
            table = pert_table(lines)
            if table:
                print(f"  [{name} / pert]")
                for t in table:
                    print(f"    {t.rstrip()}")
        mctal = case_dir / "mctal"
        if mctal.exists():
            print("  [mctal, 40 premieres lignes]")
            for t in mctal.read_text(errors="replace").splitlines()[:40]:
                print(f"    {t.rstrip()}")
        out = model_outputs(case_dir)
        if out is not None:
            print(f"  [modele MCNP.json] {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
