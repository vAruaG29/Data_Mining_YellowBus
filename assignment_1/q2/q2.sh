#!/bin/bash

GSPAN_EXE=$1
FSG_EXE=$2
GASTON_EXE=$3
DATASET=$4
OUT_DIR=$5

TIMEOUT_LIMIT=3600

mkdir -p "$OUT_DIR"

if [ ! -x "$GSPAN_EXE" ] || [ ! -x "$FSG_EXE" ] || [ ! -x "$GASTON_EXE" ]; then
    echo "ERROR: One or more binaries are not executable."
    ls -l "$GSPAN_EXE" "$FSG_EXE" "$GASTON_EXE"
    exit 1
fi

TEMP_PREFIX="$OUT_DIR/temp_dataset"

echo "Converting dataset..."
TOTAL_GRAPHS=$(python3 convert.py "$DATASET" "$TEMP_PREFIX" | tail -n 1)

if [ ! -f "$TEMP_PREFIX.gspan" ]; then
    echo "ERROR: Dataset conversion failed. $TEMP_PREFIX.gspan not found."
    exit 1
fi
echo "Total Graphs: $TOTAL_GRAPHS"

TIMING_FILE="$OUT_DIR/timing.txt"
> "$TIMING_FILE" 

SUPPORTS=(5 10 25 50 95)

for pct in "${SUPPORTS[@]}"; do
    echo "------------------------------------------------"
    echo "Processing Support: $pct%"
    
    ABS_SUPP=$(python3 -c "print(int($TOTAL_GRAPHS * $pct / 100))")
    FRAC_SUPP=$(python3 -c "print($pct / 100.0)")

    # --- Run FSG ---
    FSG_OUT="$OUT_DIR/fsg$pct"
    FSG_LOG="$OUT_DIR/fsg$pct.log"
    echo "Running FSG..."
    
    START=$(date +%s.%N)
    timeout "$TIMEOUT_LIMIT" "$FSG_EXE" -s "$pct" "$TEMP_PREFIX.fsg" > "$FSG_OUT" 2> "$FSG_LOG"
    EXIT_CODE=$?
    END=$(date +%s.%N)
    
    if [ $EXIT_CODE -eq 124 ]; then
        echo "FSG timed out > 3600s"
        RUNTIME=$TIMEOUT_LIMIT
    else
        RUNTIME=$(python3 -c "print($END - $START)")
    fi
    echo "fsg,$pct,$RUNTIME" >> "$TIMING_FILE"

    # --- Run gSpan ---
    GSPAN_OUT="$OUT_DIR/gspan$pct"
    GSPAN_LOG="$OUT_DIR/gspan$pct.log"
    echo "Running gSpan..."
    
    START=$(date +%s.%N)
    timeout "$TIMEOUT_LIMIT" "$GSPAN_EXE" -f "$TEMP_PREFIX.gspan" -s "$FRAC_SUPP" > "$GSPAN_OUT" 2> "$GSPAN_LOG"
    EXIT_CODE=$?
    END=$(date +%s.%N)
    
    if [ $EXIT_CODE -eq 124 ]; then
         echo "gSpan timed out > 3600s"
         RUNTIME=$TIMEOUT_LIMIT
    else
         RUNTIME=$(python3 -c "print($END - $START)")
    fi
    echo "gspan,$pct,$RUNTIME" >> "$TIMING_FILE"

    # --- Run Gaston ---
    GASTON_OUT="$OUT_DIR/gaston$pct"
    GASTON_LOG="$OUT_DIR/gaston$pct.log"
    echo "Running Gaston..."
    
    START=$(date +%s.%N)
    timeout "$TIMEOUT_LIMIT" "$GASTON_EXE" "$ABS_SUPP" "$TEMP_PREFIX.gspan" "$GASTON_OUT" > "$GASTON_LOG" 2>&1
    EXIT_CODE=$?
    END=$(date +%s.%N)
    
    if [ $EXIT_CODE -eq 124 ]; then
         echo "Gaston timed out > 3600s"
         RUNTIME=$TIMEOUT_LIMIT
    else
         RUNTIME=$(python3 -c "print($END - $START)")
    fi
    echo "gaston,$pct,$RUNTIME" >> "$TIMING_FILE"

done

echo "------------------------------------------------"
rm "$TEMP_PREFIX.gspan" "$TEMP_PREFIX.fsg" 2>/dev/null
echo "Generating Plot..."
python3 plot.py "$TIMING_FILE" "$OUT_DIR"
echo "Done. Results saved in $OUT_DIR"