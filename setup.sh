#!/bin/bash
# AccBlox Monitor - Automated VPS Setup Script
# This script installs all dependencies and configures the monitoring service

set -e  # Exit on error

echo "========================================"
echo "AccBlox Monitor - VPS Setup"
echo "========================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Error: Do not run this script as root${NC}"
   echo "Run as a regular user with sudo privileges"
   exit 1
fi

echo -e "${GREEN}[1/8] Updating system packages...${NC}"
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

echo -e "${GREEN}[2/8] Installing Python and dependencies...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv

echo -e "${GREEN}[3/8] Creating project directory...${NC}"
PROJECT_DIR="$HOME/accblox-monitor"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo -e "${GREEN}[4/8] Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}[5/8] Installing Python packages...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q

deactivate

echo -e "${GREEN}[6/8] Setting file permissions...${NC}"
chmod +x monitor.py
chmod 644 config.json requirements.txt

echo -e "${GREEN}[7/8] Creating systemd service...${NC}"
USERNAME=$(whoami)
SERVICE_FILE="/etc/systemd/system/accblox-monitor.service"

# Create service file with current user
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=AccBlox Product Monitor
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}[8/8] Enabling and starting service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable accblox-monitor
sudo systemctl start accblox-monitor

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Service Status:"
sudo systemctl status accblox-monitor --no-pager -l
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "1. Edit config.json and add your Telegram credentials:"
echo "   nano $PROJECT_DIR/config.json"
echo ""
echo "2. After editing config, restart the service:"
echo "   sudo systemctl restart accblox-monitor"
echo ""
echo "3. View logs:"
echo "   sudo journalctl -u accblox-monitor -f"
echo ""
echo "4. Service management:"
echo "   sudo systemctl start|stop|restart|status accblox-monitor"
echo ""
echo -e "${GREEN}Installation directory: $PROJECT_DIR${NC}"
