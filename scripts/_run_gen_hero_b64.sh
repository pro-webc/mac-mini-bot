#!/bin/sh
exec "$(dirname "$0")/../.venv/bin/python3" "$(dirname "$0")/_tmp_gen_web_png.py"
