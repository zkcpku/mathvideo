#!/bin/bash
cd "$(dirname "$0")/.."
source .venv/bin/activate

cleanup() {
    pkill -f "fish_overlay.py"
    exit 0
}

trap cleanup INT TERM

python fish_anim/fish_overlay.py &
PID=$!
wait $PID
