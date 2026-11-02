#!/usr/bin/env bash
# Build first; choose method 01..10. Each run records automatically.
set -eo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
method="${1:?Usage: bash scripts/run_comparison.sh 01 [--diagnose-stop NEW_DIRECTORY] [launch arguments]}"
shift
exec bash "$project_dir/scripts/run_dynamic.sh" --comparison "$method" "$@"
