#!/bin/bash

# This script automates updating and reinstalling the LoopBloom CLI
# from your local git repository.
# Intended for contributors who frequently run the tool directly from
# source.
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
# 1. Pull the latest changes from the 'main' branch so the local clone is
# up to date before reinstalling.
echo "Pulling latest changes..."
git pull origin main

echo "------------------------------------"

# 2. Re-install the Python package in the current environment using pip.
# This allows testing the CLI just like an end user would.
echo "Re-installing the loopbloom-cli package..."
pip install .

echo "------------------------------------"
echo "✅ Update and re-installation complete!"
# Remind the contributor how to invoke the freshly installed CLI.
echo "You can now run 'loopbloom --help' to test the changes."
