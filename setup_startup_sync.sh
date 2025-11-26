#!/bin/bash
# setup_startup_sync.sh - Setup sync to run on system startup with internet retry

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="/etc/systemd/system/leetcode-sync.service"

echo "Setting up LeetCode sync on startup..."
echo "Project directory: $PROJECT_DIR"
echo ""

# Create systemd service file
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=LeetCode to Notion Sync - Runs on startup when internet is available
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/run_sync.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created at: $SERVICE_FILE"
echo ""

# Reload systemd daemon
sudo systemctl daemon-reload
echo "✓ Systemd daemon reloaded"
echo ""

# Enable the service
sudo systemctl enable leetcode-sync.service
echo "✓ Service enabled (will run on every startup)"
echo ""

# Show status
echo "Service status:"
sudo systemctl status leetcode-sync.service
echo ""

echo "How it works:"
echo "  1. System starts up"
echo "  2. Service waits for network to be online"
echo "  3. Service runs sync.py (which has retry logic for internet)"
echo "  4. Logs are written to systemd journal and sync.log"
echo ""

echo "To view logs:"
echo "  sudo journalctl -u leetcode-sync.service -f"
echo ""

echo "To manually run the sync now:"
echo "  $PROJECT_DIR/run_sync.sh"
echo ""

echo "To disable the service:"
echo "  sudo systemctl disable leetcode-sync.service"
