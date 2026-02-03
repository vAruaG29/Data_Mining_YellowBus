#!/bin/bash


python3 -m venv venv


source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing required packages..."
pip install numpy networkx scipy joblib rustworkx

echo ""
echo "======================================"
echo "Environment setup complete!"
echo "======================================"
echo ""
echo "Installed packages:"
pip list | grep -E "numpy|networkx|scipy|joblib|rustworkx"
