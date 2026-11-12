#!/usr/bin/env bash
# Select a simulation after build. The shared runner records every invocation.
set -eo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mode="${1:?Usage: bash scripts/run_simulation.sh street|dynamic|static|paper1|paper2|paper3|paper4|paper5|paper6|paper7|paper8|compare01|compare02|compare03|compare04|compare05|compare06 [launch arguments]}"
shift
case "$mode" in
  street) exec bash "$project_dir/scripts/run_street.sh" "$@" ;;
  dynamic|static|paper1|paper2)
    exec bash "$project_dir/scripts/run_dynamic.sh" --profile "$mode" "$@" ;;
  compare01|compare02|compare03|compare04|compare05|compare06)
    exec bash "$project_dir/scripts/run_comparison.sh" "${mode#compare}" "$@" ;;
  paper3|paper4|paper5|paper6|paper7|paper8)
    paper_index="${mode#paper}"
    printf -v method '%02d' "$((10#$paper_index - 2))"
    exec bash "$project_dir/scripts/run_comparison.sh" "$method" "$@" ;;
  *) echo 'Unknown mode. Available: street, dynamic, static, paper1..paper8; compare01..compare06' >&2; exit 2 ;;
esac
