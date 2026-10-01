#!/bin/bash
# Thomas-Term: The Autonomous Offline Apex-Force Interpreter Terminal Launch Engine

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE}" )" && pwd )"
cd "$REPO_ROOT"

# Clear the canvas immediately so it's a completely black screen for the typewriter
if [ -x "$(command -v clear)" ]; then
    clear
fi

if [ -f "./python" ]; then
    # Launch the custom binary in silent, clean mode
    exec ./python -S -B
else
    echo "Error: Custom interpreter binary not found."
    echo "Please run 'make -j4' inside this folder before booting the offline terminal."
    exit 1
fi

