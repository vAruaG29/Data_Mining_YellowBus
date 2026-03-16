#!/bin/bash
# forest_fire.sh — wrapper for the route-blocking solver
# Usage: bash forest_fire.sh <graph> <seed_set> <output> <k> <n_random_instances> <hops>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$SCRIPT_DIR/forest_fire_solver.py" "$@"
