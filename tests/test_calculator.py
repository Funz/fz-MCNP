"""Tests of .fz/calculators/MCNP.sh with a fake mcnp6 executable.

The fake executable records its arguments and replays the reference outputs
of tests/fixtures (outp, mctal) under the name given by o=. Its exit code is
0 whatever the outcome (the real exit code is not relied upon, see
tests/mcnp_probe hypothesis H4).

Run: pytest tests/test_calculator.py
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".fz" / "calculators" / "MCNP.sh"
FIXTURES = ROOT / "tests" / "fixtures"

FAKE = """#!/bin/bash
printf '%s\\n' "$@" > "$(dirname "$0")/args.txt"
echo "DATAPATH=$DATAPATH" > "$(dirname "$0")/env.txt"
out=outp
for a in "$@"; do case "$a" in o=*) out="${a#o=}" ;; esac; done
case "$FAKE_CASE" in
  none) exit 0 ;;
  truncated) head -n 200 "$FIXTURES/mcnp6.1/ok_godiva/outp" > "$out"; exit 0 ;;
  *) cp "$FIXTURES/$FAKE_CASE/outp" "$out"
     [ -f "$FIXTURES/$FAKE_CASE/mctal" ] && cp "$FIXTURES/$FAKE_CASE/mctal" mctal
     exit ${FAKE_RC:-0} ;;
esac
"""

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash required")


@pytest.fixture
def fake(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    exe = bindir / "mcnp6"
    exe.write_text(FAKE)
    exe.chmod(0o755)
    return exe


@pytest.fixture
def run(tmp_path, fake):
    case_dir = tmp_path / "case"
    case_dir.mkdir()

    def _run(fake_case="mcnp6.1/ok_godiva", files=("godiva.inp",), env=None, args=None,
             use_cmd=True):
        for name in files:
            (case_dir / name).write_text("input\n")
        full_env = dict(os.environ, FAKE_CASE=fake_case, FIXTURES=str(FIXTURES))
        for k in ("MCNP_CMD", "MCNP_PATH", "MCNP_TASKS", "MCNP_OPTS", "DATAPATH"):
            full_env.pop(k, None)
        if use_cmd:
            full_env["MCNP_CMD"] = str(fake)
        full_env.update(env or {})
        proc = subprocess.run(["bash", str(SCRIPT)] + list(args if args is not None else files),
                              cwd=case_dir, env=full_env, capture_output=True, text=True)
        args_file = fake.parent / "args.txt"
        launched = args_file.read_text().split("\n")[:-1] if args_file.exists() else None
        return proc, launched

    return _run


def test_single_input_file(run):
    """fz passes the compiled input file as the only argument."""
    proc, args = run()
    assert proc.returncode == 0, proc.stderr
    assert args == ["i=godiva.inp", "o=outp"]


def test_input_without_extension(run):
    """Legacy inputs have no extension (e.g. 'godiva')."""
    proc, args = run(files=("godiva",))
    assert proc.returncode == 0, proc.stderr
    assert args[0] == "i=godiva"


def test_input_extension_preferred(run):
    """With several files, a recognized extension wins over argument order."""
    proc, args = run(files=("srcdata", "case.i"))
    assert proc.returncode == 0, proc.stderr
    assert args[0] == "i=case.i"


def test_output_files_are_not_inputs(run):
    proc, args = run(files=("outp", "runtpe.h5", "case"))
    assert args[0] == "i=case"


def test_directory_argument(run):
    proc, args = run(args=["."])
    assert proc.returncode == 0, proc.stderr
    assert args[0] == "i=godiva.inp"


def test_tasks_and_options(run):
    _, args = run(env={"MCNP_TASKS": "8", "MCNP_OPTS": "ix"})
    assert args == ["i=godiva.inp", "o=outp", "tasks", "8", "ix"]


def test_stale_outputs_removed(run, tmp_path):
    """A previous outp would be kept by MCNP (new output in outq) and parsed instead."""
    case_dir = tmp_path / "case"
    (case_dir / "outp").write_text("stale\n run terminated when 1 kcode cycles were done.\n")
    (case_dir / "mctal").write_text("stale\n")
    proc, _ = run()
    assert proc.returncode == 0
    assert "stale" not in (case_dir / "outp").read_text()
    assert not (case_dir / "mctal").exists()


@pytest.mark.parametrize("case,message", [
    ("mcnp6.3/err_no_mcard", "fatal error.  no m card for material no. 1"),
    ("mcnp6.3/err_ksrc_outside", "the entire source was rejected"),
    ("mcnp6.3/err_missing_blank", "unexpected eof"),
    ("mcnp6.3/err_lost", "run terminated because  17 particles got lost"),
    ("mcnp6.3/err_zaid_z_a", "cross-section tables missing for zaid = 24028.00c"),
    ("mcnp6.3/var_ksrc_nonfissile", "the new source has overrun the old source"),
])
def test_abnormal_end(run, case, message):
    proc, _ = run(case)
    assert proc.returncode == 6
    assert message in proc.stderr


def test_no_active_cycle(run):
    """kct <= ikz: normal end banner, no final keff (MCNP 6.3.0, hypothesis H17)."""
    proc, _ = run("mcnp6.3/err_kct_le_ikz")
    assert proc.returncode == 0
    assert "no final keff estimate" in proc.stderr


def test_echoed_input_is_not_an_error(run):
    proc, _ = run("synthetic/trap_echo")
    assert proc.returncode == 0, proc.stderr


def test_no_outp(run):
    proc, _ = run("none")
    assert proc.returncode == 5
    assert "no outp" in proc.stderr


def test_outp_without_end_banner(run):
    proc, _ = run("truncated")
    assert proc.returncode == 7


def test_nonzero_exit_code_with_normal_end(run):
    proc, _ = run(env={"FAKE_RC": "3"})
    assert proc.returncode == 0
    assert "exit code 3" in proc.stderr


def test_no_input(run):
    proc, _ = run(files=("outp",))
    assert proc.returncode == 1


def test_usage(tmp_path):
    proc = subprocess.run(["bash", str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True)
    assert proc.returncode == 2


def test_executable_not_found(run, tmp_path):
    env = {"MCNP_CMD": str(tmp_path / "missing" / "mcnp6")}
    proc, _ = run(env=env)
    assert proc.returncode == 4


def test_mcnp_path_legacy_layout(run, tmp_path, fake):
    """MCNP_PATH/MCNP_CODE/bin/mcnp6 (layout of the Java plugin) and MCNP_PATH/MCNP_DATA."""
    root = tmp_path / "MCNP6"
    (root / "MCNP_CODE" / "bin").mkdir(parents=True)
    (root / "MCNP_DATA").mkdir()
    shutil.copy(fake, root / "MCNP_CODE" / "bin" / "mcnp6")
    env = {"MCNP_PATH": str(root), "PATH": "/usr/bin:/bin"}
    proc, _ = run(env=env, use_cmd=False)
    assert proc.returncode == 0, proc.stderr
    env_txt = (root / "MCNP_CODE" / "bin" / "env.txt").read_text()
    assert env_txt.strip() == f"DATAPATH={root / 'MCNP_DATA'}"


def test_user_datapath_kept(run, fake):
    proc, _ = run(env={"DATAPATH": "/my/xsdir/dir"})
    assert proc.returncode == 0
    assert (fake.parent / "env.txt").read_text().strip() == "DATAPATH=/my/xsdir/dir"


def test_script_syntax():
    assert subprocess.run(["bash", "-n", str(SCRIPT)]).returncode == 0
