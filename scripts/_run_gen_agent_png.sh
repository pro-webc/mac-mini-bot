#!/bin/sh
exec /usr/bin/python3 "$(dirname "$0")/_gen_agent_telecom_png_b64.py" "${1:-}"
