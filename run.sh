#!/bin/bash
# docky - Convenience launcher for the distributed compute framework
# This is a thin wrapper around the Python CLI entry point.
# For full functionality, use: python -m docky
#
# Usage:
#   ./run.sh [--log] [--h HOURS] [--stop] [--id NODE_ID]
#   python -m docky [--log] [--h HOURS] [--stop] [--id NODE_ID]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install dependencies if needed
if [ ! -d "$SCRIPT_DIR/src/docky/__pycache__" ] && command -v python3 >/dev/null 2>&1; then
    python3 -c "import click" 2>/dev/null || {
        echo "[docky] Installing Python dependencies..."
        pip install -q -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || \
        pip install -q -r "$SCRIPT_DIR/requirements.txt" --user 2>/dev/null || true
    }
fi

# Pass all arguments to the Python framework
exec python3 -m docky "$@"
