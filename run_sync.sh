#!/bin/bash

# Script to run LeetCode sync with internet connectivity check
# This will retry indefinitely until internet is available

PROJECT_DIR="/home/trilok-lowanshi/Resources/LeetCodeNotionProject"
LOG_FILE="$PROJECT_DIR/sync.log"

# Check if python path exists (handles both old and new location)
if [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
elif [ -f "/home/trilok-lowanshi/Resources/LeetCodeNotionProject/venv/bin/python" ]; then
    PYTHON_BIN="/home/trilok-lowanshi/Resources/LeetCodeNotionProject/venv/bin/python"
else
    PYTHON_BIN="python3"
fi

cd "$PROJECT_DIR"

echo "=== Sync started at $(date) ===" >> "$LOG_FILE"
echo "Using Python: $PYTHON_BIN" >> "$LOG_FILE"

# Run sync with retry - it will wait for internet internally
"$PYTHON_BIN" "$PROJECT_DIR/sync.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "=== Sync completed at $(date) with exit code $EXIT_CODE ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $EXIT_CODE
