#!/bin/bash
# Lance chaque cas de tests/mcnp_probe/cases avec un MCNP reel et archive
# tout ce qui est produit, pour consolider les hypotheses du plugin.
#
# Usage :
#   ./run_probe.sh [motif]
#   MCNP_CMD=/chemin/vers/mcnp6   : executable (defaut : mcnp6 dans le PATH,
#                                   sinon $MCNP_PATH/MCNP_CODE/bin/mcnp6 ou $MCNP_PATH/bin/mcnp6)
#   DATAPATH=/chemin/donnees      : repertoire de xsdir (defaut : $MCNP_PATH/MCNP_DATA s'il existe)
#   MCNP_TASKS=4                  : nombre de threads (option "tasks N")
#   MCNP_OPTS="..."               : options supplementaires de la ligne de commande
#   MCNP_LABEL=mcnp63             : suffixe de l archive
#   motif                         : filtre glob sur les noms de cas (defaut *)
#
# Le lancement reproduit celui de .fz/calculators/MCNP.sh :
#   mcnp6 i=<cas>.i o=outp [tasks N] [MCNP_OPTS]
# Cas particuliers : var_existing_outp (un outp est cree avant le calcul),
# env_bad_datapath (DATAPATH=/nonexistent).

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
if [ -z "${MCNP_CMD:-}" ]; then
  MCNP_CMD="$(command -v mcnp6 2>/dev/null)"
  for c in "${MCNP_PATH:-/nonexistent}/MCNP_CODE/bin/mcnp6" "${MCNP_PATH:-/nonexistent}/bin/mcnp6"; do
    [ -z "$MCNP_CMD" ] && [ -x "$c" ] && MCNP_CMD="$c"
  done
fi
if [ -z "$MCNP_CMD" ] || { [ ! -x "$MCNP_CMD" ] && ! command -v "$MCNP_CMD" >/dev/null 2>&1; }; then
  echo "MCNP introuvable (definir MCNP_CMD, ou MCNP_PATH, ou mettre mcnp6 dans le PATH)" >&2
  exit 1
fi
if [ -z "${DATAPATH:-}" ] && [ -n "${MCNP_PATH:-}" ] && [ -d "$MCNP_PATH/MCNP_DATA" ]; then
  export DATAPATH="$MCNP_PATH/MCNP_DATA"
fi
if [ -z "${DATAPATH:-}" ] || ! ls "$DATAPATH"/xsdir* >/dev/null 2>&1; then
  echo "Attention : aucun xsdir dans DATAPATH='${DATAPATH:-}' ; les cas risquent d'echouer (H18)" >&2
fi

TASKS=""
[ -n "${MCNP_TASKS:-}" ] && TASKS="tasks $MCNP_TASKS"
OPTS="${MCNP_OPTS:-}"
LABEL="${MCNP_LABEL:-mcnp}"
PATTERN="${1:-*}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$HERE/results-$LABEL-$STAMP"
MAX_SIZE=$((20 * 1024 * 1024))  # fichiers plus gros : remplaces par un extrait

shopt -s nullglob
MATCHES=( "$HERE"/cases/$PATTERN.i )
shopt -u nullglob
if [ ${#MATCHES[@]} -eq 0 ]; then
  echo "Aucun cas ne correspond au motif '$PATTERN' dans $HERE/cases" >&2
  echo "(cas disponibles : $(ls "$HERE"/cases | tr '\n' ' '))" >&2
  exit 1
fi

ulimit -s unlimited 2>/dev/null || ulimit -s hard 2>/dev/null || true

mkdir -p "$OUT"
{
  echo "date: $(date -Iseconds)"
  echo "uname: $(uname -a)"
  echo "MCNP_CMD: $MCNP_CMD"
  echo "MCNP_PATH: ${MCNP_PATH:-<non defini>}"
  echo "DATAPATH: ${DATAPATH:-<non defini>}"
  echo "xsdir: $(ls "${DATAPATH:-/nonexistent}" 2>/dev/null | grep -i xsdir | tr '\n' ' ')"
  echo "MCNP_TASKS: ${MCNP_TASKS:-<aucun>}   MCNP_OPTS: ${OPTS:-<aucune>}"
  echo "nproc: $(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null)"
  echo "ulimit -s: $(ulimit -s)"
  echo "awk: $(awk -W version 2>&1 | head -1) / $(awk --version 2>&1 | head -1)"
} > "$OUT/environment.txt" 2>&1

for src in "${MATCHES[@]}"; do
  name="$(basename "$src")"
  case_dir="$OUT/${name%.*}"
  mkdir -p "$case_dir"
  cp "$src" "$case_dir/"
  echo ">>> $name"
  (
    cd "$case_dir" || exit 99
    case_env=()
    case "$name" in
      var_existing_outp.i) echo "stale outp written by run_probe.sh before the run" > outp ;;
      env_bad_datapath.i)  case_env=(DATAPATH=/nonexistent) ;;
    esac
    ls -A > .files_before
    start=$(date +%s)
    env ${case_env[@]+"${case_env[@]}"} "$MCNP_CMD" i="$name" o=outp $TASKS $OPTS > stdout.txt 2> stderr.txt < /dev/null
    rc=$?
    end=$(date +%s)
    echo "$rc" > .exit_code
    echo "$((end - start))" > .duration_s
    find . -mindepth 1 -exec ls -ld {} + | awk '{print substr($1,1,1), $5, $NF}' | sort -k3 > .files_after
    # binaires de reprise inutiles pour l'analyse (listes dans .files_after)
    rm -f runtpe runtpe.h5 runtp[e-z] *.h5
    find . -type f -size +"${MAX_SIZE}"c | while read -r big; do
      { head -c 200000 "$big"; echo; echo "[... tronque ...]"; tail -c 200000 "$big"; } > "$big.truncated"
      rm -f "$big"
    done
    echo "    rc=$rc  duree=$((end - start))s"
    if grep -qiE "command not found|commande introuvable|error while loading shared libraries" stderr.txt; then
      echo "Echec d'environnement :" >&2
      cat stderr.txt >&2
      exit 98
    fi
  )
  if [ $? -eq 98 ]; then
    echo "Arret : verifier MCNP_CMD / environnement (resultats partiels dans $OUT)" >&2
    exit 2
  fi
done

python3 "$HERE/summarize.py" "$OUT" | tee "$OUT/summary.txt"

tar -czf "$OUT.tar.gz" -C "$HERE" "$(basename "$OUT")"
echo
echo "Archive a transmettre : $OUT.tar.gz"
