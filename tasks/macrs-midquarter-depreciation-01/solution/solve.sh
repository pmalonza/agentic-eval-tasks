#!/usr/bin/env bash
# Canonical runner for the reference solution. Self-locates solve.py and
# passes through the output directory; do not hard-code paths here.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${1:?usage: solve.sh <output_dir>}"
python3 "$SCRIPT_DIR/solve.py" "$OUTPUT_DIR"
