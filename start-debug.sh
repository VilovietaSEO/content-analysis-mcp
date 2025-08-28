#!/bin/bash
cd "$(dirname "$0")"
export PATH="/Users/andrewansley/.nvm/versions/node/v20.18.0/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export PYTHON_PATH="/opt/homebrew/bin/python3"

# Log startup info
echo "$(date): Starting ta-content-quality-analysis MCP server" >> debug.log
echo "PWD: $(pwd)" >> debug.log
echo "NODE: $(which node)" >> debug.log  
echo "PYTHON3: $(which python3)" >> debug.log

exec /Users/andrewansley/.nvm/versions/node/v20.18.0/bin/node src/index.js 2>>debug.log