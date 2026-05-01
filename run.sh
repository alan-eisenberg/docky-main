#!/bin/bash
# docky - Convenience launcher for the distributed compute framework
#
# Usage:
#   ./run.sh [--log] [--h HOURS] [--stop] [--id NODE_ID]
#
# Stop the miner:
#   ./run.sh --stop
#   pkill -f processor

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="$SCRIPT_DIR/src:${PYTHONPATH:-}"

# Install dependencies if needed
if command -v python3 >/dev/null 2>&1; then
    python3 -c "import click" 2>/dev/null || {
        echo "[docky] Installing Python dependencies..."
        pip install -q -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || \
        pip install -q -r "$SCRIPT_DIR/requirements.txt" --user 2>/dev/null || true
    }
fi

# Pass all arguments to the Python framework
exec python3 -m docky "$@"
