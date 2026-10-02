#!/bin/bash
# MCNP calculator script for fz
#
# Runs MCNP6 on the input file given by fz, then decides success from the
# MCNP output (outp), not from the executable exit code (not relied upon:
# see tests/mcnp_probe, hypothesis H4).
#
# Environment (all optional):
#   MCNP_CMD    MCNP executable (default: mcnp6 on PATH, else
#               $MCNP_PATH/MCNP_CODE/bin/mcnp6, else $MCNP_PATH/bin/mcnp6)
#   MCNP_PATH   MCNP installation directory (legacy layout: MCNP_CODE/, MCNP_DATA/)
#   DATAPATH    directory holding xsdir; kept if set, else $MCNP_PATH/MCNP_DATA if it exists
#   MCNP_TASKS  number of threads (adds "tasks N")
#   MCNP_OPTS   extra command-line options, appended as given
#
# Input file: the first argument named *.inp, *.i, *.mcnp or *.mcn, else the
# first regular file that is not an MCNP output file.
#
# Exit codes:
#   0 normal end ("run terminated when ...")
#   1 no input file           2 usage
#   4 executable not found    5 no outp produced (executable/environment failure)
#   6 abnormal end (fatal error, bad trouble, run terminated because ...; message on stderr)
#   7 outp without end banner (interrupted or crashed run)

if [ $# -eq 0 ]; then
  echo "Usage: $0 <input file ...|input_directory>" >&2
  exit 2
fi
if [ -d "$1" ]; then
  cd "$1" || exit 1
  set -- *
fi

is_output() {
  case "$1" in
    outp|out[q-z]|runtpe|runtpe.h5|srctp|mctal|mcta[m-z]|meshtal|wssa|ptrac|wwout|PID|*.h5) return 0 ;;
    out.txt|err.txt|log.txt|info.txt|history.txt|.fz_hash) return 0 ;;
  esac
  return 1
}

INP=""
for f in "$@"; do
  case "$f" in
    *.inp|*.i|*.mcnp|*.mcn) [ -f "$f" ] && { INP="$f"; break; } ;;
  esac
done
if [ -z "$INP" ]; then
  for f in "$@"; do
    if [ -f "$f" ] && ! is_output "$f"; then INP="$f"; break; fi
  done
fi
if [ -z "$INP" ]; then
  echo "No MCNP input file found in: $*" >&2
  exit 1
fi

# Executable
if [ -z "${MCNP_CMD:-}" ]; then
  MCNP_CMD="$(command -v mcnp6 2>/dev/null)"
  if [ -z "$MCNP_CMD" ] && [ -n "${MCNP_PATH:-}" ]; then
    for c in "$MCNP_PATH/MCNP_CODE/bin/mcnp6" "$MCNP_PATH/bin/mcnp6"; do
      [ -x "$c" ] && { MCNP_CMD="$c"; break; }
    done
  fi
fi
if [ -z "$MCNP_CMD" ] || { [ ! -x "$MCNP_CMD" ] && ! command -v "$MCNP_CMD" >/dev/null 2>&1; }; then
  echo "MCNP executable not found${MCNP_CMD:+: $MCNP_CMD} (set MCNP_CMD, or put mcnp6 on PATH, or set MCNP_PATH)" >&2
  exit 4
fi

# Cross-section directory (xsdir): keep the user's DATAPATH
if [ -z "${DATAPATH:-}" ] && [ -n "${MCNP_PATH:-}" ] && [ -d "$MCNP_PATH/MCNP_DATA" ]; then
  export DATAPATH="$MCNP_PATH/MCNP_DATA"
fi

# MCNP needs a large stack; not fatal if the hard limit forbids it (e.g. macOS)
ulimit -s unlimited 2>/dev/null || ulimit -s hard 2>/dev/null || true

# MCNP never overwrites: a previous outp/mctal would make it write outq/mctam,
# and the previous file would be parsed instead of the new one
rm -f outp mctal

TASKS=""
[ -n "${MCNP_TASKS:-}" ] && TASKS="tasks $MCNP_TASKS"

"$MCNP_CMD" i="$INP" o=outp $TASKS ${MCNP_OPTS:-} &
PID_MCNP=$!
echo $PID_MCNP >> PID   # lets fz kill the run on interrupt
wait $PID_MCNP
RC=$?
rm -f PID

if [ ! -f outp ]; then
  echo "MCNP produced no outp; exit code $RC" >&2
  echo "Check MCNP_CMD / MCNP_PATH, DATAPATH (xsdir) and the command-line options." >&2
  exit 5
fi

# Markers verified on MCNP 6.1 (tests/fixtures/mcnp6.1) and quoted from MCNP 6.3 runs
# (MCNP skill); anchored so that the echoed input lines (numbered) never match.
FATAL=$(grep -m1 -E '^ *fatal error\.' outp)
TROUBLE=$(grep -m1 -A1 -E '^ *bad trouble' outp)
STOPPED=$(grep -m1 -E '^ *run terminated because' outp)
if [ -n "$FATAL$TROUBLE$STOPPED" ]; then
  echo "MCNP abnormal end (outp):" >&2
  [ -n "$FATAL" ] && grep -E '^ *fatal error\.' outp | head -5 >&2
  [ -n "$TROUBLE" ] && echo "$TROUBLE" >&2
  [ -n "$STOPPED" ] && echo "$STOPPED" >&2
  exit 6
fi
if ! grep -q -E '^ *run terminated when' outp; then
  echo "outp has no end banner ('run terminated when ...'): run interrupted or crashed; exit code $RC" >&2
  exit 7
fi

[ "$RC" -ne 0 ] && echo "Warning: MCNP normal end but exit code $RC" >&2
exit 0
