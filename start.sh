#!/bin/bash
cd "$(dirname "$0")"
export PATH="/Users/andrewansley/.nvm/versions/node/v20.18.0/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export PYTHON_PATH="/opt/homebrew/bin/python3"
exec /Users/andrewansley/.nvm/versions/node/v20.18.0/bin/node src/index.js