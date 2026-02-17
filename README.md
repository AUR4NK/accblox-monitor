# AccBlox Product Monitor - VPS Deployment Guide

Complete guide for deploying the AccBlox product monitoring system on a VPS server.

## Table of Contents

- [Overview](#overview)
- [VPS Requirements](#vps-requirements)
- [VPS Provider Recommendations](#vps-provider-recommendations)
- [Prerequisites](#prerequisites)
- [Getting Telegram Credentials](#getting-telegram-credentials)
- [Quick Installation (Recommended)](#quick-installation-recommended)
- [Manual Setup (Without setup.sh)](#manual-setup-without-setupsh)
- [Service Management Commands](#service-management-commands)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Monitoring Performance](#monitoring-performance)
- [Updating Monitor](#updating-monitor)
- [Uninstalling](#uninstalling)
- [Configuration](#configuration)
- [Additional Notes](#additional-notes)

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
3. The bot will reply with your user information
4. **Save the Chat ID** (looks like: `1234567890`)

**Method 2: Using Your Bot**
1. Start your bot by searching for its username in Telegram
2. Send `/start` or any message to your bot
3. Visit this URL in your browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":123456789}` in the response
5. **Save that ID**

---

## Quick Installation (Recommended)

### Step 1: SSH into Your VPS

```bash
ssh root@YOUR_VPS_IP
# or
ssh your_username@YOUR_VPS_IP
```

### Step 2: Run One-Line Installer

```bash
curl -s https://raw.githubusercontent.com/AUR4NK/accblox-monitor/main/setup.sh | bash
```

### Step 3: Follow the Interactive Setup

The script will:
1. Install all dependencies automatically
2. Clone the repository
3. Ask for your Telegram credentials:
   - Telegram Bot Token
   - Telegram Chat ID
4. Configure the monitoring settings:
   - Target product name (default: "Pack 99 Infinity Block")
   - Target price (default: $130.00)
   - Check interval (default: 30 seconds)
5. Set up systemd service
6. Start the monitor automatically

### Step 4: Verify Installation

```bash
# Check service status
sudo systemctl status accblox-monitor

# View live logs
sudo journalctl -u accblox-monitor -f
```

---

## Manual Setup (Without setup.sh)

### Step 1: Prepare Your VPS
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv git
```

### Step 2: Clone Repository
```bash
# Clone from GitHub
cd ~
git clone https://github.com/AUR4NK/accblox-monitor.git
cd accblox-monitor
```

### Step 3: Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Telegram Bot

**A. Create Telegram Bot:**
1. Open Telegram and search for @BotFather
2. Send `/newbot` command
3. Follow prompts to create bot
4. Copy the Bot Token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

**B. Get Your Chat ID:**
1. Search for @userinfobot in Telegram
2. Start conversation
3. Copy your Chat ID (format: `123456789`)

**C. Update config.json:**
```bash
nano config.json
```

Edit the file:
```json
{
  "accblox_url": "https://accblox.net/",
  "target_product": "Pack 99 Infinity Block",
  "target_price": 130.00,
  "check_interval_seconds": 30,
  "telegram_bot_token": "YOUR_BOT_TOKEN_HERE",
  "telegram_chat_id": "YOUR_CHAT_ID_HERE",
  "max_duration_hours": null
}
```

Save (Ctrl+O, Enter) and exit (Ctrl+X).

### Step 5: Test Monitor Manually
```bash
# Make monitor executable
chmod +x monitor.py

# Test run (Ctrl+C to stop)
python monitor.py
```

You should see:
```
2026-02-18 01:45:30 - INFO - AccBlox Monitor initialized
2026-02-18 01:45:30 - INFO - Target: Pack 99 Infinity Block @ $130.00
2026-02-18 01:45:30 - INFO - Check interval: 30 seconds
2026-02-18 01:45:30 - INFO - Starting AccBlox Monitor...
2026-02-18 01:45:30 - INFO - Check #1 - Scraping accblox.net...
```

### Step 6: Setup Systemd Service (Auto-start)
```bash
# Deactivate venv first
deactivate

# Create service file
sudo nano /etc/systemd/system/accblox-monitor.service
```

Paste this (replace `YOUR_USERNAME` with your actual username):
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Save and exit.

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable accblox-monitor

# Start service
sudo systemctl start accblox-monitor

# Check status
sudo systemctl status accblox-monitor
```

---

## Service Management Commands

```bash
# Start monitor
sudo systemctl start accblox-monitor

# Stop monitor
sudo systemctl stop accblox-monitor

# Restart monitor (after config changes)
sudo systemctl restart accblox-monitor

# Check status
sudo systemctl status accblox-monitor

# View real-time logs
sudo journalctl -u accblox-monitor -f

# View last 50 log lines
sudo journalctl -u accblox-monitor -n 50

# View logs from today
sudo journalctl -u accblox-monitor --since today

# Disable auto-start on boot
sudo systemctl disable accblox-monitor
```

---

## Troubleshooting Guide

### Issue: "Connection refused" or "Network error"
**Solution:**
```bash
# Check internet connectivity
ping -c 3 google.com

# Test accblox.net directly
curl -I https://accblox.net/

# Check if VPS firewall blocks outgoing connections
sudo iptables -L OUTPUT
```

### Issue: "Telegram alert not sending"
**Solution:**
```bash
# Test Telegram token manually
TOKEN="your_bot_token_here"
CHAT_ID="your_chat_id_here"

curl -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\":\"$CHAT_ID\",\"text\":\"Test message\"}"

# Should return: {"ok":true,...}
```

### Issue: Service keeps restarting
**Solution:**
```bash
# View detailed error logs
sudo journalctl -u accblox-monitor -n 100 --no-pager

# Check Python errors
cd ~/accblox-monitor
source venv/bin/activate
python monitor.py  # Run manually to see errors
```

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
# Reinstall dependencies
cd ~/accblox-monitor
source venv/bin/activate
pip install --force-reinstall -r requirements.txt
deactivate
sudo systemctl restart accblox-monitor
```

### Issue: High CPU usage
**Solution:**
```bash
# Increase check interval in config.json
nano config.json
# Change "check_interval_seconds" from 30 to 60 or higher

# Restart service
sudo systemctl restart accblox-monitor
```

### Issue: Monitor not detecting product
**Solution:**
```bash
# Enable debug mode - edit monitor.py
nano monitor.py
# Change logging level from INFO to DEBUG at line 15

# Check what products are being scraped
sudo journalctl -u accblox-monitor -f

# Verify target_product and target_price in config.json match exactly
nano config.json
```

---

## Monitoring Performance

```bash
# View statistics (check every 5 minutes)
sudo journalctl -u accblox-monitor -n 100 | grep "Stats:"

# Monitor CPU/Memory usage
top -p $(pgrep -f "accblox-monitor")

# Check disk usage for logs
du -sh ~/accblox-monitor/monitor.log
sudo journalctl --disk-usage
```

---

## Updating Monitor

```bash
# Stop service
sudo systemctl stop accblox-monitor

# Pull latest changes
cd ~/accblox-monitor
git pull origin main

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Restart service
sudo systemctl start accblox-monitor
```

---

## Uninstalling

```bash
# Stop and disable service
sudo systemctl stop accblox-monitor
sudo systemctl disable accblox-monitor

# Remove service file
sudo rm /etc/systemd/system/accblox-monitor.service
sudo systemctl daemon-reload

# Remove project directory
rm -rf ~/accblox-monitor
```

---

## Configuration

### Modifying Settings

```bash
# Edit configuration
cd ~/accblox-monitor
nano config.json
```

Available options:

```json
{
  "accblox_url": "https://accblox.net/",
  "target_product": "Pack 99 Infinity Block",
  "target_price": 130.00,
  "check_interval_seconds": 30,
  "telegram_bot_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID",
  "max_duration_hours": null
}
```

**Configuration Options:**

- **accblox_url**: Website to scrape (usually no need to change)
- **target_product**: Exact product name to search for (case-sensitive)
- **target_price**: Maximum price to trigger alert
- **check_interval_seconds**: How often to check (30 = every 30 seconds)
- **telegram_bot_token**: Your Telegram bot token from BotFather
- **telegram_chat_id**: Your Telegram user ID
- **max_duration_hours**: Optional - stop after X hours (null = run forever)

After changing config:

```bash
# Restart service to apply changes
sudo systemctl restart accblox-monitor

# Check if it's running
sudo systemctl status accblox-monitor
```

---

## Additional Notes

### Security Recommendations

1. **Use a non-root user** for running the service
2. **Keep your VPS updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
3. **Enable firewall:**
   ```bash
   sudo ufw allow ssh
   sudo ufw enable
   ```
4. **Protect your Telegram credentials** - don't share config.json

### Performance Tips

- For faster response: reduce `check_interval_seconds` (but increases load)
- For lower resource usage: increase `check_interval_seconds`
- Monitor runs very light - typically <1% CPU, ~50MB RAM

### Multiple Products

To monitor multiple products, you can:
1. Clone the repository to different folders
2. Use different config.json for each
3. Create separate systemd services

Example:
```bash
cp -r ~/accblox-monitor ~/accblox-monitor-product2
# Edit config in product2 folder
# Create new service file with different name
```

---

## License

MIT License - feel free to modify and use for your needs.

---

## Support

For issues or questions:
- Check [Troubleshooting Guide](#troubleshooting-guide) section above
- Review logs: `sudo journalctl -u accblox-monitor -n 100`
- Open an issue on GitHub

---

**Happy monitoring! 🚀**
