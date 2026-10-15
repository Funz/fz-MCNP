"""End-to-end run through fz (fzr) with a fake mcnp6 replaying the real MCNP 6.1 output.

Checks the whole chain: calculator alias discovery (localhost_MCNP), the
arguments fz passes to MCNP.sh (one compiled input file), output parsing.

Run: pytest tests/test_fz_e2e.py
"""

import os
import shutil
from pathlib import Path

import pytest

fz = pytest.importorskip("fz")

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "mcnp6.1" / "ok_godiva"

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash required")


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    shutil.copytree(ROOT / ".fz", tmp_path / ".fz")
    shutil.copy(ROOT / "examples" / "godiva.inp", tmp_path)
    fake = tmp_path / "bin" / "mcnp6"
    fake.parent.mkdir()
    fake.write_text(
        "#!/bin/bash\n"
        "for a in \"$@\"; do case \"$a\" in i=*) inp=\"${a#i=}\" ;; o=*) out=\"${a#o=}\" ;; esac; done\n"
        "grep -q 'so 8.741' \"$inp\" || { echo 'radius not substituted' >&2; exit 1; }\n"
        f"cp '{FIXTURE / 'outp'}' \"$out\"\n")
    fake.chmod(0o755)
    monkeypatch.setenv("MCNP_CMD", str(fake))
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize("calculators", ["localhost_MCNP", None])
def test_fzr(workspace, calculators):
    kwargs = {"calculators": calculators} if calculators else {}
    results = fz.fzr("godiva.inp", {"r": [8.741]}, "MCNP",
                     results_dir=str(workspace / "results"), **kwargs)
    row = results.iloc[0]
    assert row["status"] == "done", row.to_dict()
    assert row["mcnp_status"] == "NORMAL END"
    assert float(row["mean_keff"]) == pytest.approx(1.00248)
    assert float(row["sigma_keff"]) == pytest.approx(0.00062)


def test_fzr_failed_case(workspace):
    """A run that produces no outp is reported as failed (MCNP.sh exit code 5)."""
    results = fz.fzr("godiva.inp", {"r": [9.0]}, "MCNP", calculators="localhost_MCNP",
                     results_dir=str(workspace / "results"))
    row = results.iloc[0]
    assert row["status"] != "done"
    assert row["mcnp_status"] == "NO OUTPUT"
