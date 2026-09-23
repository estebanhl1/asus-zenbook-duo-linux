#!/usr/bin/env bash
# Compatibility entry point: historically this installed the complete setup.
set -euo pipefail
exec bash "$(dirname -- "${BASH_SOURCE[0]}")/install.sh" all "$@"
