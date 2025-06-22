#!/bin/bash

# This script automates updating and reinstalling the LoopBloom CLI
# from your local git repository.
#
# Place this script in the root directory of your cloned repository.

set -e

# Get the directory where the script is located, which we assume
# is the root of the repository.
REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navigate to the repository directory
cd "${REPO_DIR}" || exit

echo "Navigated to: $(pwd)"
echo "------------------------------------"

# 1. Pull the latest changes from the 'main' branch
echo "Pulling latest changes..."
git pull origin main

echo "------------------------------------"

# 2. Re-install the Python package
# Based on the pyproject.toml, the project can be installed with pip.
echo "Re-installing the loopbloom-cli package..."
pip install .

echo "------------------------------------"
echo "✅ Update and re-installation complete!"
echo "You can now run 'loopbloom --help' to test the changes."
