#!/bin/bash
# setup_daily_sync.sh - Setup automatic daily sync

# Get the current directory (your project folder)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/sync.py"
LOG_FILE="$PROJECT_DIR/sync.log"

echo "Setting up daily LeetCode to Notion sync..."
echo "Project directory: $PROJECT_DIR"

# Create a wrapper script that logs output
cat > "$PROJECT_DIR/run_sync.sh" << EOF
#!/bin/bash
cd $PROJECT_DIR
echo "=== Sync started at \$(date) ===" >> $LOG_FILE
$PYTHON_PATH $SCRIPT_PATH >> $LOG_FILE 2>&1
echo "=== Sync completed at \$(date) ===" >> $LOG_FILE
echo "" >> $LOG_FILE
EOF

# Make the wrapper script executable
chmod +x "$PROJECT_DIR/run_sync.sh"

# Create cron job (runs daily at 11:00 PM)
CRON_JOB="0 23 * * * $PROJECT_DIR/run_sync.sh"

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -v "$PROJECT_DIR/run_sync.sh"; echo "$CRON_JOB") | crontab -

echo ""
echo "✓ Setup complete!"
echo ""
echo "Your sync will run automatically every day at 11:00 PM"
echo "Logs will be saved to: $LOG_FILE"
echo ""
echo "To change the time, edit the cron job:"
echo "  crontab -e"
echo ""
echo "Current cron schedule:"
crontab -l | grep run_sync.sh
echo ""
echo "To test the sync manually, run:"
echo "  $PROJECT_DIR/run_sync.sh"