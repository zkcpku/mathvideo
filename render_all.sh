#!/bin/bash
export PATH="/Library/TeX/texbin:$PATH"
cd "$(dirname "$0")"
source .venv/bin/activate

QUALITY="${1:--ql}"

echo "Rendering all scenes with quality: $QUALITY"
python stacktrans/render_all.py "$QUALITY"
