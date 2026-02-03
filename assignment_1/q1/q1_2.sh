#!/bin/bash
set -e

SCRIPT="gen_dataset_plateau.py"   
ITEMS="$1"
TRANSACTIONS="$2"

CMD="python3 $SCRIPT"
if [ -n "$ITEMS" ]; then
    CMD="$CMD $ITEMS"
fi

if [ -n "$TRANSACTIONS" ]; then
    CMD="$CMD $TRANSACTIONS"
fi

echo "Running:"
echo "  $CMD"
echo

exec $CMD
