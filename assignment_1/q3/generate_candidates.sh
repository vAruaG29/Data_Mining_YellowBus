#!/bin/bash



if [ "$#" -ne 3 ]; then
    echo "Usage: bash generate_candidates.sh <path_database_graph_features> <path_query_graph_features> <path_out_file>"
    exit 1
fi

DB_FEATURES=$1
QUERY_FEATURES=$2
OUTPUT_FILE=$3


source venv/bin/activate


python3 -u generate_candidates.py "$DB_FEATURES" "$QUERY_FEATURES" "$OUTPUT_FILE"
