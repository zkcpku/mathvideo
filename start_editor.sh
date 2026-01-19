#!/bin/bash
export PATH="/Library/TeX/texbin:$PATH"
cd "$(dirname "$0")"
source .venv/bin/activate
manedit
