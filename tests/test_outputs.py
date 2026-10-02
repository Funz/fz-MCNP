"""Output extraction of the MCNP model.

Fixtures:
- tests/fixtures/mcnp6.1/: real MCNP 6.1 run (Godiva, from the Java plugin-MCNP test case;
  XSDIR path anonymized);
- tests/fixtures/synthetic/: outputs rebuilt from the messages quoted in the MCNP skill
  (reproduced with MCNP 6.3.0 according to the skill); to be replaced by real outputs of
  tests/mcnp_probe (see tests/fixtures/README.md).

Run: pytest tests/test_outputs.py
"""

import json
import math
import shutil
from pathlib import Path

import pytest

fz = pytest.importorskip("fz")

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
MODEL = json.loads((ROOT / ".fz" / "models" / "MCNP.json").read_text())

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash required")


def outputs(path):
    return fz.fzo(str(path), MODEL).iloc[0].to_dict()


def missing(value):
    return value is None or (isinstance(value, float) and math.isnan(value))


# --- real MCNP 6.1 output ---

def test_keff_real_mcnp61():
    out = outputs(FIXTURES / "mcnp6.1" / "ok_godiva")
    assert out["mcnp_status"] == "NORMAL END"
    assert float(out["mean_keff"]) == pytest.approx(1.00248, abs=1e-6)
    assert float(out["sigma_keff"]) == pytest.approx(0.00062, abs=1e-6)


def test_keff_matches_stdout_summary():
    """Independent check: the terminal summary printed by MCNP (out.txt)."""
    d = FIXTURES / "mcnp6.1" / "ok_godiva"
    line = next(l for l in (d / "out.txt").read_text().splitlines() if "final k(col/abs/trk len)" in l)
    keff, std = float(line.split("=")[1].split()[0]), float(line.split("=")[2])
    out = outputs(d)
    assert float(out["mean_keff"]) == keff
    assert float(out["sigma_keff"]) == std


def test_no_pert_no_tally_columns():
    out = outputs(FIXTURES / "mcnp6.1" / "ok_godiva")
    assert not any(k.startswith(("dkeff", "sigma_dkeff", "tally")) for k in out)


def test_no_end_banner(tmp_path):
    lines = (FIXTURES / "mcnp6.1" / "ok_godiva" / "outp").read_text().splitlines()[:200]
    (tmp_path / "outp").write_text("\n".join(lines) + "\n")
    out = outputs(tmp_path)
    assert out["mcnp_status"] == "NO END BANNER"
    assert missing(out["mean_keff"])


def test_no_output(tmp_path):
    (tmp_path / "godiva.inp").write_text("input only\n")
    assert outputs(tmp_path)["mcnp_status"] == "NO OUTPUT"


def test_status_from_stdout_when_no_outp(tmp_path):
    """Errors raised before outp is written are still reported from fz's out.txt."""
    (tmp_path / "out.txt").write_text(
        " bad trouble in subroutine ixsdir of imcn\n data file xsdir_mcnp6.3 does not exist.\n")
    assert outputs(tmp_path)["mcnp_status"] == (
        "BAD TROUBLE: data file xsdir_mcnp6.3 does not exist. (subroutine ixsdir of imcn)")


# --- synthetic outputs (MCNP 6.3 messages quoted in the skill) ---

@pytest.mark.parametrize("case,status", [
    ("err_no_mcard", "FATAL ERROR: no m card for material no. 1"),
    ("err_ksrc_outside", "FATAL ERROR: the entire source was rejected."),
    ("err_missing_blank", "BAD TROUBLE: unexpected eof in file case.i (subroutine pass0 of imcn)"),
    ("err_lost", "ABNORMAL END: run terminated because 10 particles got lost."),
])
def test_abnormal_status(case, status):
    out = outputs(FIXTURES / "synthetic" / case)
    assert out["mcnp_status"] == status
    assert missing(out["mean_keff"])
    assert missing(out["sigma_keff"])


def test_echoed_input_does_not_fool_status():
    out = outputs(FIXTURES / "synthetic" / "trap_echo")
    assert out["mcnp_status"] == "NORMAL END"
    assert float(out["mean_keff"]) == pytest.approx(1.00248)


def test_pert():
    out = outputs(FIXTURES / "synthetic" / "ok_pert")
    assert float(out["mean_keff"]) == pytest.approx(0.998611)
    assert float(out["sigma_keff"]) == pytest.approx(0.001769)
    assert out["dkeff_1"] == pytest.approx(0.00830)
    assert out["dkeff_2"] == pytest.approx(-0.00840)
    assert out["dkeff_3"] == pytest.approx(-0.00031)
    assert out["sigma_dkeff_3"] == pytest.approx(0.00064)


def test_tally_mctal_last_bin():
    """Last (mean, relative error) pair of each tally = total bin when the tally has one."""
    out = outputs(FIXTURES / "synthetic" / "ok_tally")
    assert out["mcnp_status"] == "NORMAL END"
    assert out["tally_2"] == pytest.approx(1.64800e-04)
    assert out["tally_relerr_2"] == pytest.approx(0.0377)
    assert out["tally_4"] == pytest.approx(2.5e-05)
    assert out["tally_relerr_4"] == pytest.approx(0.0123)
    assert missing(out["mean_keff"])
