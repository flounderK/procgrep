#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

mkdir -p "$HOME/.local/bin"

if [ -e "$SCRIPT_DIR/requirements.txt" ];then
	pip install -r "$SCRIPT_DIR/requirements.txt"
fi

install "$SCRIPT_DIR/procgrep.py" "$HOME/.local/bin"
