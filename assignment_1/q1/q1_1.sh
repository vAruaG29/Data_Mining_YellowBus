#!/bin/bash
set +e

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <path_apriori> <path_fp> <path_dataset> <path_out>"
    exit 1
fi

# Variables
APRIORI_BIN="$1"
FPGROWTH_BIN="$2"
DATASET="$3"
OUTDIR="$4"
RESULTS="results.csv"
TMAX=3600
SUPPORTS=(90 50 25 10 5)

mkdir -p "$OUTDIR"
echo "Algorithm,Support,TimeSeconds" > "$RESULTS"

run_mining() {
    local alg=$1
    local sup=$2
    local bin=$3

    local prefix
    if [ "$alg" = "Apriori" ]; then
        prefix="ap"
    elif [ "$alg" = "FP-Growth" ]; then
        prefix="fp"
    else
        echo "Unknown algorithm: $alg"
        return 1
    fi

    local outfile="$OUTDIR/${prefix}${sup}.txt"
    : > "$outfile"

    echo "Running $alg at ${sup}% support..."

    start=$(date +%s%N)
    timeout ${TMAX}s "$bin" -s"$sup" "$DATASET" "$outfile"
    status=$?
    end=$(date +%s%N)

    elapsed_ns=$((end - start))
    elapsed=$(awk "BEGIN { printf \"%.3f\", $elapsed_ns/1e9 }")

    if [ $status -eq 124 ]; then
        echo "$alg,$sup,$TMAX" >> "$RESULTS"
        echo "The timeout (${TMAX}s) occurred for the ${sup}% support threshold." > "$outfile"
    else
        echo "$alg,$sup,$elapsed" >> "$RESULTS"
    fi

}


# Main Execution Loop
for sup in "${SUPPORTS[@]}"; do
    run_mining "Apriori" "$sup" "$APRIORI_BIN"
    run_mining "FP-Growth" "$sup" "$FPGROWTH_BIN"
done

# Call the separate Python Plotting script
if command -v python3 &>/dev/null; then
    python3 plot.py "$RESULTS" "$OUTDIR"
else
    echo "Python3 not found. Skipping plot generation."
fi

echo "All tasks complete."