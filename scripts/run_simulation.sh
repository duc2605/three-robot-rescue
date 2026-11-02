#!/usr/bin/env bash
# Select a simulation after build. The shared runner records every invocation.
set -eo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mode="${1:?Usage: bash scripts/run_simulation.sh dynamic|static|paper1..paper12|compare01..compare10 [launch arguments]}"
shift
case "$mode" in
  dynamic|static|paper1|paper2)
    exec bash "$project_dir/scripts/run_dynamic.sh" --profile "$mode" "$@" ;;
  compare0[1-9]|compare10)
    exec bash "$project_dir/scripts/run_comparison.sh" "${mode#compare}" "$@" ;;
  paper[3-9]|paper1[0-2])
    paper_index="${mode#paper}"
    printf -v method '%02d' "$((10#$paper_index - 2))"
    exec bash "$project_dir/scripts/run_comparison.sh" "$method" "$@" ;;
  *) echo 'Unknown mode: choose dynamic, static, paper1..paper12 or compare01..compare10' >&2; exit 2 ;;
esac
