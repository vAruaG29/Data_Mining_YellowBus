#!/bin/bash



if [ "$#" -ne 3 ]; then
    echo "Usage: bash convert.sh <path_graphs> <path_discriminative_subgraphs> <path_features>"
    exit 1
fi

GRAPHS_PATH=$1
SUBGRAPHS_PATH=$2
OUTPUT_PATH=$3


source venv/bin/activate

python3 -u convert_to_features.py "$GRAPHS_PATH" "$SUBGRAPHS_PATH" "$OUTPUT_PATH"
