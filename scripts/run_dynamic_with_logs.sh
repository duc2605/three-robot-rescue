#!/usr/bin/env bash
# Compatibility entry point: ordinary simulation, no diagnostic session logs.
set -eo pipefail
exec bash "$(dirname "${BASH_SOURCE[0]}")/run_dynamic.sh" "$@"
