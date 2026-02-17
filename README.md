# AccBlox Product Monitor - VPS Deployment Guide

Complete guide for deploying the AccBlox product monitoring system on a VPS server.

## Table of Contents

- [Overview](#overview)
- [VPS Requirements](#vps-requirements)
- [VPS Provider Recommendations](#vps-provider-recommendations)
- [Prerequisites](#prerequisites)
- [Getting Telegram Credentials](#getting-telegram-credentials)
- [Quick Installation (Recommended)](#quick-installation-recommended)
- [Manual Installation](#manual-installation)
- [Service Management](#service-management)
- [Monitoring and Logs](#monitoring-and-logs)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Overview

This monitoring system:
- Scrapes accblox.net every 30 seconds
- Searches for specific product name and price
- Sends Telegram alerts when target is found
- Runs as a systemd service (auto-restart on failure, starts on boot)
- Logs all activity with timestamps and statistics

---

## VPS Requirements

**Minimum Specifications:**
- **OS:** Ubuntu 20.04 LTS or newer (Debian 10+ also works)
- **RAM:** 512 MB (1 GB recommended)
- **Storage:** 5 GB
- **CPU:** 1 vCPU
- **Network:** Stable internet connection

**Estimated Cost:** $3-5 USD/month

---

## VPS Provider Recommendations

### Budget-Friendly Options

1. **DigitalOcean** (Recommended)
   - $4/month for 512MB RAM droplet
   - Website: https://www.digitalocean.com
   - Easy setup, excellent documentation
   - $200 free credit for new users (60 days)

2. **Vultr**
   - $3.50/month for 512MB RAM instance
   - Website: https://www.vultr.com
   - Fast deployment, multiple locations
   - $100 free credit for new users

3. **Linode (Akamai)**
   - $5/month for 1GB RAM instance
   - Website: https://www.linode.com
   - Reliable, good performance
   - $100 free credit for new users

4. **Contabo**
   - $4.50/month for 4GB RAM VPS
   - Website: https://contabo.com
   - Best value for resources
   - No free trial

5. **Hetzner**
   - 4.15 EUR/month for CX11 (2GB RAM)
   - Website: https://www.hetzner.com
   - European provider, excellent price/performance

---

## Prerequisites

Before starting, you need:

1. **VPS Server** with SSH access (root or sudo user)
2. **Telegram Bot Token** (see below)
3. **Telegram Chat ID** (see below)

---

## Getting Telegram Credentials

### Step 1: Get Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/start` to BotFather
3. Send `/newbot` to create a new bot
4. Follow the instructions:
   - Choose a name for your bot (e.g., "AccBlox Monitor")
   - Choose a username (e.g., "accblox_monitor_bot")
5. BotFather will send you a **Bot Token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
6. **Save this token** - you'll need it during installation

### Step 2: Get Your Chat ID

**Method 1: Using @userinfobot (Recommended)**
1. Open Telegram and search for **@userinfobot**
2. Send `/start` to the bot
3. The bot will reply with your **Chat ID** (a number like `123456789` or `-1001234567890`)
4. **Save this Chat ID** - you'll need it during installation

**Method 2: Using @RawDataBot**
1. Search for **@RawDataBot** in Telegram
2. Send any message to the bot
3. Look for `"id":` in the response - that's your Chat ID

**Method 3: Send a message to your bot and check**
1. Search for your bot by username in Telegram
2. Send `/start` to your bot
3. Open this URL in your browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":` - that's your Chat ID

---

## Quick Installation (Recommended)

This automated script handles everything for you.

### Step 1: Connect to Your VPS

```bash
ssh your_username@your_vps_ip
```

### Step 2: Download the Package

Upload all files to your VPS, or create them manually:

```bash
# Create directory
mkdir -p ~/accblox-monitor-package
cd ~/accblox-monitor-package

# Upload files here (using scp, sftp, or paste content)
# You need: monitor.py, config.json, requirements.txt, setup.sh
```

**OR** download from your repository (if hosted):

```bash
git clone YOUR_REPO_URL ~/accblox-monitor-package
cd ~/accblox-monitor-package
```

### Step 3: Run the Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

The script will:
1. Install Python3, pip, and dependencies
2. Create installation directory at `~/accblox-monitor`
3. Setup virtual environment
4. Ask for your Telegram credentials
5. Create and start the systemd service

### Step 4: Verify Installation

```bash
sudo systemctl status accblox-monitor
```

You should see "active (running)" in green.

**That's it! The monitor is now running 24/7.**

---

## Manual Installation

If the automated script fails, follow these steps:

### Step 1: Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
```

### Step 2: Create Installation Directory

```bash
mkdir -p ~/accblox-monitor
cd ~/accblox-monitor
```

### Step 3: Create Files

Create each file manually (copy content from the package):

**monitor.py:**
```bash
nano monitor.py
# Paste content, then Ctrl+X, Y, Enter
chmod +x monitor.py
```

**config.json:**
```bash
nano config.json
# Paste content, update telegram_bot_token and telegram_chat_id
# Ctrl+X, Y, Enter
```

**requirements.txt:**
```bash
nano requirements.txt
# Paste content, then Ctrl+X, Y, Enter
```

### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

### Step 5: Edit Configuration

```bash
nano config.json
```

Update these fields:
- `telegram_bot_token`: Your bot token from BotFather
- `telegram_chat_id`: Your chat ID from @userinfobot

### Step 6: Test the Monitor

```bash
source venv/bin/activate
python monitor.py
```

Press `Ctrl+C` to stop after verifying it works.

### Step 7: Create Systemd Service

```bash
sudo nano /etc/systemd/system/accblox-monitor.service
```

Paste this content (replace `YOUR_USERNAME` with your actual username):

```ini
[Unit]
Description=AccBlox Product Monitor
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/accblox-monitor
ExecStart=/home/YOUR_USERNAME/accblox-monitor/venv/bin/python monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 8: Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable accblox-monitor
sudo systemctl start accblox-monitor
```

### Step 9: Verify Service

```bash
sudo systemctl status accblox-monitor
```

---

## Service Management

### Check Service Status

```bash
sudo systemctl status accblox-monitor
```

### Start Service

```bash
sudo systemctl start accblox-monitor
```

### Stop Service

```bash
sudo systemctl stop accblox-monitor
```

### Restart Service

```bash
sudo systemctl restart accblox-monitor
```

### Enable Service (Auto-start on boot)

```bash
sudo systemctl enable accblox-monitor
```

### Disable Service (Don't auto-start)

```bash
sudo systemctl disable accblox-monitor
```

---

## Monitoring and Logs

### View Live Logs (Real-time)

```bash
sudo journalctl -u accblox-monitor -f
```

Press `Ctrl+C` to stop.

### View Recent Logs

```bash
sudo journalctl -u accblox-monitor -n 100
```

### View Logs Since Boot

```bash
sudo journalctl -u accblox-monitor -b
```

### View Monitor Log File

```bash
tail -f ~/accblox-monitor/monitor.log
```

### Check Statistics

The monitor prints statistics every 10 checks. View them in the logs:

```bash
tail -100 ~/accblox-monitor/monitor.log | grep "MONITORING STATISTICS" -A 10
```

---

## Configuration

Edit the configuration file to change settings:

```bash
cd ~/accblox-monitor
nano config.json
```

### Available Settings

```json
{
  "accblox_url": "https://accblox.net/",
  "target_product": "Pack 99 Infinity Block",
  "target_price": "130.00",
  "check_interval_seconds": 30,
  "telegram_bot_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID",
  "max_duration_hours": null
}
```

**Settings Explained:**

- `accblox_url`: Website to monitor
- `target_product`: Product name to search for (case-insensitive)
- `target_price`: Price to match (without $ symbol)
- `check_interval_seconds`: How often to check (30 = every 30 seconds)
- `telegram_bot_token`: Your Telegram bot token
- `telegram_chat_id`: Your Telegram chat ID
- `max_duration_hours`: Max hours to run (null = run forever)

**After changing config, restart the service:**

```bash
sudo systemctl restart accblox-monitor
```

---

## Troubleshooting

### Service Won't Start

**Check the service status:**
```bash
sudo systemctl status accblox-monitor -l
```

**Check for errors in logs:**
```bash
sudo journalctl -u accblox-monitor -n 50
```

**Common issues:**
- Wrong username in service file
- Missing Python dependencies
- Invalid config.json (check JSON syntax)
- Wrong file permissions

### No Telegram Alerts

**Test your bot token and chat ID:**
```bash
cd ~/accblox-monitor
source venv/bin/activate
python3 << EOF
import requests
import json

with open('config.json') as f:
    config = json.load(f)

url = f"https://api.telegram.org/bot{config['telegram_bot_token']}/sendMessage"
payload = {
    'chat_id': config['telegram_chat_id'],
    'text': 'Test message from AccBlox Monitor'
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())
EOF
```

If you see `200` and `"ok": true`, your credentials are correct.

### High CPU/Memory Usage

**Check resource usage:**
```bash
top -p $(pgrep -f monitor.py)
```

**Increase check interval to reduce CPU:**
```bash
nano ~/accblox-monitor/config.json
# Change check_interval_seconds to 60 or higher
sudo systemctl restart accblox-monitor
```

### Target Not Being Detected

**Test the scraper manually:**
```bash
cd ~/accblox-monitor
source venv/bin/activate
python3 << EOF
import requests
from bs4 import BeautifulSoup

response = requests.get('https://accblox.net/')
soup = BeautifulSoup(response.text, 'lxml')

# Search for product
for element in soup.find_all(['div', 'span', 'h1', 'h2', 'h3', 'p', 'a']):
    text = element.get_text(strip=True)
    if 'Pack 99' in text or '130' in text:
        print(f"Found: {text}")
EOF
```

This will show what the scraper can find on the page.

### Permission Denied Errors

**Fix file permissions:**
```bash
cd ~/accblox-monitor
chmod +x monitor.py
chmod 644 config.json requirements.txt
```

### Python Module Not Found

**Reinstall dependencies:**
```bash
cd ~/accblox-monitor
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
sudo systemctl restart accblox-monitor
```

### Service Keeps Restarting

**Check if config.json is valid:**
```bash
cd ~/accblox-monitor
python3 -c "import json; json.load(open('config.json'))"
```

If no error, config is valid.

**Check monitor.py syntax:**
```bash
cd ~/accblox-monitor
python3 -m py_compile monitor.py
```

### View Full Error Messages

```bash
sudo journalctl -u accblox-monitor -n 200 --no-pager
```

---

## Updating the Monitor

To update the monitor code:

```bash
# Stop the service
sudo systemctl stop accblox-monitor

# Backup current version
cp ~/accblox-monitor/monitor.py ~/accblox-monitor/monitor.py.backup

# Update monitor.py (upload new version or edit)
nano ~/accblox-monitor/monitor.py

# Restart the service
sudo systemctl start accblox-monitor

# Check status
sudo systemctl status accblox-monitor
```

---

## Uninstalling

To completely remove the monitor:

```bash
# Stop and disable service
sudo systemctl stop accblox-monitor
sudo systemctl disable accblox-monitor

# Remove service file
sudo rm /etc/systemd/system/accblox-monitor.service
sudo systemctl daemon-reload

# Remove installation directory
rm -rf ~/accblox-monitor

# (Optional) Remove Python packages
sudo apt-get remove python3-venv
```

---

## Support

If you encounter issues not covered in this guide:

1. Check the logs: `sudo journalctl -u accblox-monitor -n 100`
2. Test the configuration manually
3. Verify Telegram credentials
4. Check VPS network connectivity: `ping google.com`
5. Ensure website is accessible: `curl -I https://accblox.net/`

---

## Summary

**Installation Path:** `~/accblox-monitor`  
**Service Name:** `accblox-monitor.service`  
**Log File:** `~/accblox-monitor/monitor.log`  
**Config File:** `~/accblox-monitor/config.json`

**Key Commands:**
```bash
# Start monitoring
sudo systemctl start accblox-monitor

# View live logs
sudo journalctl -u accblox-monitor -f

# Check status
sudo systemctl status accblox-monitor

# Edit config
nano ~/accblox-monitor/config.json

# Restart after config change
sudo systemctl restart accblox-monitor
```

---

**The monitor will run 24/7 and send you a Telegram alert when the target product is found!**
