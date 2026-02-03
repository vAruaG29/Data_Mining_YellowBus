#!/bin/bash


if [ "$#" -ne 2 ]; then
    echo "Usage: bash identify.sh <path_graph_dataset> <path_discriminative_subgraphs>"
    exit 1
fi

GRAPH_DATASET=$1
OUTPUT_PATH=$2

source venv/bin/activate

python3 -u identify_subgraphs.py "$GRAPH_DATASET" "$OUTPUT_PATH"
