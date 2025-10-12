#!/bin/bash

# MCNP calculator script for fz
# This script runs MCNP calculations

# Check if MCNP_PATH is set
if [ -z "$MCNP_PATH" ]; then
  echo "Error: MCNP_PATH environment variable is not set"
  echo "Please set MCNP_PATH to your MCNP installation directory"
  echo "Example: export MCNP_PATH=/Applications/MCNP6"
  exit 1
fi

# Check if MCNP executable exists
if [ ! -f "$MCNP_PATH/MCNP_CODE/bin/mcnp6" ]; then
  echo "Error: MCNP executable not found at $MCNP_PATH/MCNP_CODE/bin/mcnp6"
  exit 1
fi

# Set DATAPATH for MCNP data files
export DATAPATH="$MCNP_PATH/MCNP_DATA"

# Set unlimited stack size (required for MCNP)
ulimit -s unlimited

# If directory as input, cd into it
if [ -d "$1" ]; then
  cd "$1"
  INP=`ls *.inp 2>/dev/null | head -n 1`
  if [ -z "$INP" ]; then
    INP=`ls * 2>/dev/null | grep -v '\.o$\|\.r$\|\.s$\|outp$\|runtpe$\|srctp$' | head -n 1`
  fi
  shift
# If $* are files, find the input file
elif [ $# -gt 1 ]; then
  INP=""
  for f in "$@"; do
    if [ -f "$f" ]; then
      INP="$f"
      break
    fi
  done
  if [ -z "$INP" ]; then
    echo "No input file found. Exiting."
    exit 1
  fi
  shift $#
else
  echo "Usage: $0 <input_file or input_directory>"
  exit 2
fi

# Store process ID for tracking
echo $$ >> PID

# Run MCNP with the input file
$MCNP_PATH/MCNP_CODE/bin/mcnp6 inp=$INP &
PID_MCNP=$!
echo $PID_MCNP >> PID
wait $PID_MCNP

# Clean up PID file
if [ -f "PID" ]; then
  rm -f "PID"
fi
