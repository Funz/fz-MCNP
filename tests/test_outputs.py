"""Output extraction of the MCNP model.

Fixtures:
- tests/fixtures/mcnp6.1/: real MCNP 6.1 run (Godiva, from the Java plugin-MCNP test case;
  XSDIR path anonymized);
- tests/fixtures/mcnp6.3/: real MCNP 6.3.0 runs of tests/mcnp_probe (data paths anonymized);
- tests/fixtures/synthetic/trap_echo: hand-written trap (error messages in the echoed input).

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


# --- real MCNP 6.3.0 outputs (tests/mcnp_probe, ENDF/B-VII.1 / ENDF/B-VIII.0 site libraries) ---

@pytest.mark.parametrize("case,status", [
    ("err_no_mcard", "FATAL ERROR: no m card for material no. 1"),
    ("err_ksrc_outside", "FATAL ERROR: the entire source was rejected."),
    ("err_missing_blank", "BAD TROUBLE: unexpected eof in file err_missing_blank.i (subroutine pass0 of imcn)"),
    ("err_lost", "ABNORMAL END: run terminated because 17 particles got lost."),
    # fatal error printed before "bad trouble in subroutine rhoden": fatal error wins
    ("err_zaid_z_a", "FATAL ERROR: cross-section tables missing for zaid = 24028.00c"),
    # reason two non-blank lines after the "bad trouble" line
    ("var_ksrc_nonfissile", "BAD TROUBLE: the new source has overrun the old source. "
                            "(subroutine colidk of mcrun, source particle no. 6400)"),
    # end banner of a normal run, but no active cycle
    ("err_kct_le_ikz", "NO KEFF: no final keff estimate made because no active cycles run."),
    # no outp: message on the terminal only (fz out.txt)
    ("err_line_128", "BAD TROUBLE: input file data beyond column 128. (subroutine exemes of mcnp)"),
])
def test_abnormal_status(case, status):
    out = outputs(FIXTURES / "mcnp6.3" / case)
    assert out["mcnp_status"] == status
    assert missing(out["mean_keff"])
    assert missing(out["sigma_keff"])


def test_ctme_is_normal_end():
    """'run terminated when it had used 0.3 minutes of computer time.' (CTME, kct = 0)."""
    out = outputs(FIXTURES / "mcnp6.3" / "ok_ctme")
    assert out["mcnp_status"] == "NORMAL END"
    assert float(out["mean_keff"]) == pytest.approx(0.999444)
    assert float(out["sigma_keff"]) == pytest.approx(0.000496)


def test_echoed_input_does_not_fool_status():
    """Synthetic by nature: messages quoted in comments of the echoed input."""
    out = outputs(FIXTURES / "synthetic" / "trap_echo")
    assert out["mcnp_status"] == "NORMAL END"
    assert float(out["mean_keff"]) == pytest.approx(1.00248)


def test_pert():
    out = outputs(FIXTURES / "mcnp6.3" / "ok_pert")
    assert out["mcnp_status"] == "NORMAL END"
    assert float(out["mean_keff"]) == pytest.approx(0.999412)
    assert float(out["sigma_keff"]) == pytest.approx(0.001147)
    assert out["dkeff_1"] == pytest.approx(0.00802)
    assert out["dkeff_2"] == pytest.approx(-0.00807)
    assert out["sigma_dkeff_1"] == pytest.approx(0.00004)
    assert out["sigma_dkeff_2"] == pytest.approx(0.00004)
    assert "dkeff_3" not in out


def test_tally_mctal_kcode():
    """F4 tallies without energy bins: one (mean, relative error) pair each."""
    out = outputs(FIXTURES / "mcnp6.3" / "ok_tally_kcode")
    assert out["mcnp_status"] == "NORMAL END"
    assert out["tally_4"] == pytest.approx(2.42105e-03)
    assert out["tally_relerr_4"] == pytest.approx(0.0012)
    assert out["tally_14"] == pytest.approx(1.37484e-04)
    assert out["tally_relerr_14"] == pytest.approx(0.0012)


def test_tally_mctal_fixed_source_total_bin():
    """F2 with 6 energy bounds: 'et 7', last pair = total bin (equals the last tfc value)."""
    d = FIXTURES / "mcnp6.3" / "ok_fixed_source"
    out = outputs(d)
    assert out["mcnp_status"] == "NORMAL END"
    assert out["tally_2"] == pytest.approx(3.55903e-05)
    assert out["tally_relerr_2"] == pytest.approx(0.0080)
    assert out["tally_4"] == pytest.approx(2.36035e-04)
    assert out["tally_relerr_4"] == pytest.approx(0.0015)
    assert missing(out["mean_keff"])
    tfc_last = [l.split() for l in (d / "mctal").read_text().splitlines() if l.startswith(" " * 9)]
    assert float(tfc_last[12][1]) == out["tally_2"]


@pytest.mark.parametrize("case", ["ok_pert", "ok_fixed_source", "var_ksrc_nonfissile", "err_kct_le_ikz"])
def test_crlf_line_ends(tmp_path, case):
    """Same values from files with Windows line ends (CRLF)."""
    src = FIXTURES / "mcnp6.3" / case
    for f in src.iterdir():
        (tmp_path / f.name).write_bytes(f.read_bytes().replace(b"\n", b"\r\n"))
    def values(d):
        return {k: None if missing(v) else v for k, v in outputs(d).items() if k != "path"}
    assert values(tmp_path) == values(src)
