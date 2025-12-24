#!/bin/bash
# IHEP Virtual Environment Setup Script
# Creates and populates a Python virtual environment with all dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/venv}"

echo "=== IHEP Virtual Environment Setup ==="
echo "Project root: $PROJECT_ROOT"
echo "Venv location: $VENV_DIR"
echo ""

# Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    read -p "Delete and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
    else
        echo "Using existing venv..."
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from all requirements files
echo ""
echo "Installing dependencies..."

REQUIREMENTS_FILES=(
    "applications/backend/requirements.txt"
    "curriculum-backend/requirements.txt"
    "services/chat-api/requirements.txt"
    "services/health-api/requirements.txt"
)

for req_file in "${REQUIREMENTS_FILES[@]}"; do
    full_path="$PROJECT_ROOT/$req_file"
    if [ -f "$full_path" ]; then
        echo ""
        echo "Installing from $req_file..."
        pip install -r "$full_path"
    else
        echo "Warning: $req_file not found, skipping..."
    fi
done

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To activate the virtual environment, run:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To deactivate, run:"
echo "  deactivate"
