# Shadow Trading Machine - Complete Setup Guide

> **Purpose:** Step-by-step guide to set up a dedicated machine for running shadow trading validation of EXP-009 Hybrid LLM Strategy

**Target:** Fresh Linux/Mac/Windows machine dedicated to automated shadow trading
**Timeline:** 1-2 hours setup
**Cost:** $0 (uses free/open-source software)

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Operating System Setup](#operating-system-setup)
3. [Python Environment](#python-environment)
4. [Project Setup](#project-setup)
5. [API Configuration](#api-configuration)
6. [Testing & Validation](#testing--validation)
7. [Automation Setup](#automation-setup)
8. [Monitoring & Logging](#monitoring--logging)
9. [Cost Tracking](#cost-tracking)
10. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Specs
- **CPU:** 2 cores (any modern processor)
- **RAM:** 4GB
- **Storage:** 10GB free space
- **Internet:** Stable connection (shadow trading requires real-time data)
- **OS:** Linux (Ubuntu 22.04 recommended), macOS 12+, or Windows 10+

### Recommended Specs
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 20GB SSD
- **Internet:** Wired connection (more reliable than WiFi)

### Why Dedicated Machine?
- ✅ Runs 24/7 without interrupting your main computer
- ✅ Isolated environment (no conflicts with other projects)
- ✅ Can be a cheap mini PC or Raspberry Pi ($100-200)
- ✅ Easier to monitor and debug

---

## Operating System Setup

### Option 1: Ubuntu 22.04 LTS (Recommended)

**Why Ubuntu?**
- Free, stable, well-documented
- Excellent for automation and server applications
- Low resource usage

**Installation:**

```bash
# 1. Download Ubuntu Server or Desktop
https://ubuntu.com/download/server

# 2. Create bootable USB (use Rufus on Windows, dd on Linux/Mac)
# 3. Install Ubuntu on dedicated machine
# 4. During installation:
#    - Create user: tradingbot
#    - Enable SSH server (for remote access)
#    - No extra packages needed initially
```

**Post-Install Setup:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    screen \
    build-essential

# Set timezone (important for market hours)
sudo timedatectl set-timezone America/New_York  # Or your timezone

# Verify time is correct
timedatectl
```

---

### Option 2: macOS (If You Have a Spare Mac)

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install essential tools
brew install git python@3.11 wget

# Set timezone
sudo systemsetup -settimezone America/New_York
```

---

### Option 3: Windows 10/11 with WSL2

```powershell
# 1. Enable WSL2
wsl --install

# 2. Install Ubuntu 22.04 from Microsoft Store
# 3. Follow Ubuntu setup above inside WSL2
```

---

## Python Environment

### Install Python 3.11+

**Ubuntu/Debian:**
```bash
# Add Python PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Set as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verify installation
python3.11 --version  # Should show 3.11.x
pip3.11 --version
```

**macOS:**
```bash
brew install python@3.11
python3.11 --version
```

---

## Project Setup

### Clone Repository

```bash
# Create workspace directory
mkdir -p ~/trading
cd ~/trading

# Clone the repository
git clone https://github.com/neimasilk/modular-quant-backtest.git
cd modular-quant-backtest

# Checkout the correct branch
git checkout claude/review-docs-next-steps-yfiWP  # Or main branch

# Verify files are there
ls -la
```

---

### Create Python Virtual Environment

```bash
# Create venv
python3.11 -m venv venv

# Activate venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install additional dependencies for shadow trading
pip install \
    yfinance \
    openai \
    python-dotenv \
    requests \
    beautifulsoup4 \
    pandas \
    numpy

# Verify installation
pip list
```

---

## API Configuration

### 1. Get DeepSeek API Key

**Sign Up:**
1. Visit: https://platform.deepseek.com/
2. Click "Sign Up" → Create account with email
3. Verify email
4. Navigate to "API Keys" section
5. Click "Create New Key"
6. Copy the key (starts with `sk-...`)
7. **IMPORTANT:** Save this key securely! You can't view it again.

**Pricing (as of 2026-01):**
- DeepSeek V2: ~$0.14 per 1M input tokens
- DeepSeek V2: ~$0.28 per 1M output tokens
- **Estimated cost:** $0.10-0.30 per LLM call
- **Shadow trading:** ~5-20 calls/day = $1-5/day

**Free Credits:**
- New accounts usually get $5-10 free credits
- Enough for ~50-100 shadow trading calls

---

### 2. Create .env File

```bash
cd ~/trading/modular-quant-backtest

# Create .env file
cat > .env << 'EOF'
# DeepSeek API Configuration
DEEPSEEK_API_KEY=sk-your-actual-key-here

# Shadow Trading Configuration
SHADOW_TRADING_ENABLED=true
SHADOW_TRADING_TICKERS=NVDA,AAPL,TSLA
SHADOW_TRADING_VOLATILITY_THRESHOLD=0.03
SHADOW_TRADING_MAX_CALLS_PER_DAY=20

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/shadow_trading.log

# Timezone
TZ=America/New_York
EOF

# Replace with your actual API key
nano .env  # Edit the file, paste your real key

# Set secure permissions (only you can read)
chmod 600 .env

# Verify
cat .env | grep DEEPSEEK_API_KEY
# Should show: DEEPSEEK_API_KEY=sk-...
```

**Security Notes:**
- ⚠️ NEVER commit .env file to git
- ⚠️ NEVER share your API key
- ⚠️ Set restrictive file permissions (chmod 600)
- ✅ .env is already in .gitignore (safe)

---

### 3. Test API Connection

```bash
# Activate venv if not already
source venv/bin/activate

# Test DeepSeek API
python << 'EOF'
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    print("❌ API key not found in .env file")
    exit(1)

print(f"✅ API key loaded: {api_key[:10]}...")

# Test API call
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "Say 'Shadow trading API test successful!' and nothing else."}
        ],
        max_tokens=20
    )

    message = response.choices[0].message.content
    print(f"✅ API Response: {message}")
    print("✅ DeepSeek API is working!")

except Exception as e:
    print(f"❌ API test failed: {e}")
    exit(1)
EOF
```

**Expected Output:**
```
✅ API key loaded: sk-1234567...
✅ API Response: Shadow trading API test successful!
✅ DeepSeek API is working!
```

---

## Testing & Validation

### Test 1: Shadow Trading Script

```bash
cd experiments/active/EXP-2025-009-hybrid-llm

# Run quick test (1 ticker, 5 days)
python shadow_trading.py --ticker NVDA --days 5

# Expected output:
# ✅ LLM Sanity Checker initialized
# 📊 Fetching 5 days of data for NVDA...
# 🔍 Analyzing NVDA on 2026-01-XX
#   Price change: +X.X%
#   News: ...
#   🤖 LLM: BUY_TREND (score: X/10)
# 💾 Results saved to: shadow_logs/...
```

**If it works:** ✅ Proceed to automation

**If it fails:** See [Troubleshooting](#troubleshooting) section

---

### Test 2: Multi-Ticker Test

```bash
# Test with 3 tickers, 10 days
python shadow_trading.py --ticker NVDA,AAPL,TSLA --days 10

# Check results
ls -lh shadow_logs/
cat shadow_logs/shadow_decisions_*.json | head -50
```

---

### Test 3: Cost Tracking

```bash
# Count LLM calls
cat shadow_logs/shadow_decisions_*.json | grep '"llm_call_time"' | wc -l

# Estimate cost (assuming $0.20/call average)
# Example: 15 calls × $0.20 = $3.00
```

---

## Automation Setup

### Create Shadow Trading Runner Script

```bash
cd ~/trading/modular-quant-backtest

# Create automation script
cat > run_shadow_trading.sh << 'EOF'
#!/bin/bash

# Shadow Trading Automation Script
# Runs daily shadow trading analysis

set -e  # Exit on error

# Configuration
PROJECT_DIR="$HOME/trading/modular-quant-backtest"
VENV_DIR="$PROJECT_DIR/venv"
SCRIPT_DIR="$PROJECT_DIR/experiments/active/EXP-2025-009-hybrid-llm"
LOG_DIR="$PROJECT_DIR/logs"
TICKERS="NVDA,AAPL,TSLA"
DAYS=5

# Create log directory
mkdir -p "$LOG_DIR"

# Log file with timestamp
LOG_FILE="$LOG_DIR/shadow_trading_$(date +%Y%m%d_%H%M%S).log"

echo "==================================================" | tee -a "$LOG_FILE"
echo "Shadow Trading Run - $(date)" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Change to script directory
cd "$SCRIPT_DIR"

# Run shadow trading
echo "Running shadow trading for: $TICKERS" | tee -a "$LOG_FILE"

python shadow_trading.py \
    --ticker "$TICKERS" \
    --days "$DAYS" \
    2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Shadow trading completed successfully" | tee -a "$LOG_FILE"
else
    echo "❌ Shadow trading failed with exit code $EXIT_CODE" | tee -a "$LOG_FILE"
fi

# Deactivate venv
deactivate

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "shadow_trading_*.log" -mtime +30 -delete

echo "Log saved to: $LOG_FILE"

exit $EXIT_CODE
EOF

# Make executable
chmod +x run_shadow_trading.sh

# Test it
./run_shadow_trading.sh
```

---

### Schedule with Cron (Linux/Mac)

**Daily shadow trading at 5:30 PM (after market close):**

```bash
# Edit crontab
crontab -e

# Add this line (adjust path if different):
30 17 * * 1-5 cd $HOME/trading/modular-quant-backtest && ./run_shadow_trading.sh

# Format: minute hour day month dayofweek command
# 30 17 * * 1-5 = 5:30 PM, Monday-Friday

# Verify cron job
crontab -l
```

**Cron Schedule Examples:**

```bash
# Daily at 5:30 PM (weekdays only)
30 17 * * 1-5 /path/to/run_shadow_trading.sh

# Daily at 9:00 AM (before market open)
0 9 * * 1-5 /path/to/run_shadow_trading.sh

# Every 6 hours (for testing)
0 */6 * * * /path/to/run_shadow_trading.sh

# Check cron logs
sudo tail -f /var/log/syslog | grep CRON  # Ubuntu
tail -f /var/log/cron                      # CentOS/RHEL
```

---

### Alternative: systemd Timer (More Reliable)

**Create systemd service:**

```bash
sudo tee /etc/systemd/system/shadow-trading.service << 'EOF'
[Unit]
Description=Shadow Trading Analysis
After=network.target

[Service]
Type=oneshot
User=tradingbot
WorkingDirectory=/home/tradingbot/trading/modular-quant-backtest
ExecStart=/home/tradingbot/trading/modular-quant-backtest/run_shadow_trading.sh
StandardOutput=journal
StandardError=journal
EOF

# Create systemd timer
sudo tee /etc/systemd/system/shadow-trading.timer << 'EOF'
[Unit]
Description=Run shadow trading daily at 5:30 PM

[Timer]
OnCalendar=Mon-Fri 17:30:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable shadow-trading.timer
sudo systemctl start shadow-trading.timer

# Check status
sudo systemctl status shadow-trading.timer

# View upcoming runs
systemctl list-timers shadow-trading.timer

# Manual run (for testing)
sudo systemctl start shadow-trading.service
```

---

## Monitoring & Logging

### View Logs in Real-Time

```bash
# Follow latest log file
tail -f logs/shadow_trading_*.log

# View systemd logs
sudo journalctl -u shadow-trading.service -f

# View cron execution
sudo tail -f /var/log/syslog | grep shadow
```

---

### Create Monitoring Dashboard Script

```bash
cat > shadow_trading_status.sh << 'EOF'
#!/bin/bash

# Shadow Trading Status Dashboard

PROJECT_DIR="$HOME/trading/modular-quant-backtest"
LOG_DIR="$PROJECT_DIR/logs"
SHADOW_LOG_DIR="$PROJECT_DIR/experiments/active/EXP-2025-009-hybrid-llm/shadow_logs"

echo "=========================================="
echo "   SHADOW TRADING STATUS DASHBOARD"
echo "=========================================="
echo ""

# Last run
echo "📅 Last Run:"
ls -lt "$LOG_DIR"/shadow_trading_*.log | head -1 | awk '{print "   "$6,$7,$8,$9}'

# Total runs
echo ""
echo "📊 Statistics:"
echo "   Total runs: $(ls "$LOG_DIR"/shadow_trading_*.log 2>/dev/null | wc -l)"
echo "   Total LLM calls: $(cat "$SHADOW_LOG_DIR"/shadow_decisions_*.json 2>/dev/null | grep -c '"llm_call_time"')"

# Recent decisions
echo ""
echo "🔍 Recent Decisions (last 5):"
ls -t "$SHADOW_LOG_DIR"/shadow_decisions_*.json | head -1 | xargs cat | \
    jq -r '.decisions[-5:][] | "   \(.date) \(.ticker): \(.llm_signal) (score: \(.substance_score)/10)"' 2>/dev/null || echo "   No data yet"

# Cost estimate
total_calls=$(cat "$SHADOW_LOG_DIR"/shadow_decisions_*.json 2>/dev/null | grep -c '"llm_call_time"' || echo 0)
cost=$(echo "$total_calls * 0.20" | bc)
echo ""
echo "💰 Estimated Cost:"
echo "   Total LLM calls: $total_calls"
echo "   Estimated cost: \$$cost (@ \$0.20/call)"

# Disk usage
echo ""
echo "💾 Disk Usage:"
echo "   Logs: $(du -sh "$LOG_DIR" 2>/dev/null | cut -f1)"
echo "   Shadow data: $(du -sh "$SHADOW_LOG_DIR" 2>/dev/null | cut -f1)"

# Next scheduled run
echo ""
echo "⏰ Next Scheduled Run:"
if command -v systemctl &> /dev/null; then
    systemctl list-timers shadow-trading.timer 2>/dev/null | grep shadow || echo "   Not scheduled (cron?)"
else
    echo "   Check crontab -l for schedule"
fi

echo ""
echo "=========================================="
EOF

chmod +x shadow_trading_status.sh

# Run it
./shadow_trading_status.sh
```

---

## Cost Tracking

### Create Cost Tracker

```bash
cat > track_costs.py << 'EOF'
#!/usr/bin/env python3
"""
Shadow Trading Cost Tracker

Analyzes shadow trading logs to calculate actual API costs.
"""

import json
import glob
from pathlib import Path
from datetime import datetime

# Cost per LLM call (approximate)
COST_PER_CALL = 0.20  # USD

def analyze_costs():
    shadow_logs = glob.glob(
        'experiments/active/EXP-2025-009-hybrid-llm/shadow_logs/shadow_decisions_*.json'
    )

    if not shadow_logs:
        print("⚠️ No shadow trading logs found")
        return

    total_calls = 0
    dates = []

    for log_file in shadow_logs:
        with open(log_file, 'r') as f:
            data = json.load(f)

        calls_in_file = len(data.get('decisions', []))
        total_calls += calls_in_file

        # Extract date from filename
        filename = Path(log_file).name
        date_str = filename.split('_')[2]  # shadow_decisions_YYYYMMDD_...
        dates.append(date_str)

    total_cost = total_calls * COST_PER_CALL

    print(f"📊 Shadow Trading Cost Analysis")
    print(f"="*50)
    print(f"Total runs: {len(shadow_logs)}")
    print(f"Date range: {min(dates)} to {max(dates)}")
    print(f"Total LLM calls: {total_calls}")
    print(f"Average calls/day: {total_calls / len(set(dates)):.1f}")
    print(f"")
    print(f"💰 Cost Breakdown:")
    print(f"Cost per call: ${COST_PER_CALL:.2f}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Daily average: ${total_cost / len(set(dates)):.2f}")
    print(f"")
    print(f"📅 Projection (30 days):")
    daily_avg = total_cost / len(set(dates)) if dates else 0
    print(f"Monthly cost: ${daily_avg * 30:.2f}")

if __name__ == '__main__':
    analyze_costs()
EOF

chmod +x track_costs.py
python track_costs.py
```

---

## Troubleshooting

### Issue 1: API Key Not Found

**Symptoms:**
```
❌ DEEPSEEK_API_KEY not found in environment
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check .env content
cat .env | grep DEEPSEEK_API_KEY

# If missing, create .env file (see API Configuration section)

# Verify environment variable is loaded
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DEEPSEEK_API_KEY'))"
```

---

### Issue 2: Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'openai'
```

**Solution:**
```bash
# Activate venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
pip install openai python-dotenv yfinance

# Verify
pip list | grep openai
```

---

### Issue 3: Permission Denied

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/home/user/...'
```

**Solution:**
```bash
# Fix file permissions
chmod +x run_shadow_trading.sh
chmod +x shadow_trading_status.sh

# Fix directory permissions
chmod 755 ~/trading
chmod 755 ~/trading/modular-quant-backtest

# Fix log directory
mkdir -p logs
chmod 755 logs
```

---

### Issue 4: Cron Not Running

**Symptoms:**
- Script doesn't run at scheduled time
- No logs generated

**Solution:**
```bash
# Check cron service is running
sudo systemctl status cron  # Ubuntu/Debian
sudo systemctl status crond # CentOS/RHEL

# Check cron logs
sudo tail -50 /var/log/syslog | grep CRON

# Test script manually first
cd ~/trading/modular-quant-backtest
./run_shadow_trading.sh

# If manual run works but cron doesn't, check:
# 1. Full paths in crontab (don't use ~, use $HOME or /home/user)
# 2. Environment variables may not be available in cron
# 3. Use absolute paths for everything
```

---

### Issue 5: API Rate Limiting

**Symptoms:**
```
❌ Rate limit exceeded
```

**Solution:**
```bash
# Reduce tickers or frequency
# Edit .env file:
SHADOW_TRADING_TICKERS=NVDA  # Only 1 ticker instead of 3
SHADOW_TRADING_MAX_CALLS_PER_DAY=10  # Reduce from 20

# Add delays between calls (edit shadow_trading.py)
import time
time.sleep(5)  # Wait 5 seconds between calls
```

---

## Advanced: Remote Access Setup (Optional)

**SSH Access from Anywhere:**

```bash
# On shadow trading machine:
# 1. Install SSH server (if not already)
sudo apt install openssh-server

# 2. Start SSH service
sudo systemctl enable ssh
sudo systemctl start ssh

# 3. Get IP address
ip addr show | grep "inet "

# 4. From your laptop:
ssh tradingbot@<machine-ip>

# 5. Optional: Setup SSH key for passwordless login
ssh-keygen -t ed25519
ssh-copy-id tradingbot@<machine-ip>
```

**Port Forwarding for Home Network:**
- Forward port 22 (SSH) on your router to shadow trading machine
- Use dynamic DNS service (like DuckDNS) for consistent hostname

---

## Maintenance

### Weekly Tasks

```bash
# 1. Check logs
./shadow_trading_status.sh

# 2. Check costs
python track_costs.py

# 3. Verify accuracy (manual review)
ls -t experiments/active/EXP-2025-009-hybrid-llm/shadow_logs/*.json | head -1 | xargs cat | jq '.decisions[-10:]'

# 4. Update code (if needed)
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

### Monthly Tasks

```bash
# 1. Analyze results
cd experiments/active/EXP-2025-009-hybrid-llm
python shadow_trading.py --report

# 2. Clean old logs (keep last 60 days)
find logs/ -name "*.log" -mtime +60 -delete

# 3. Backup data
tar -czf shadow_trading_backup_$(date +%Y%m%d).tar.gz \
    experiments/active/EXP-2025-009-hybrid-llm/shadow_logs/ \
    logs/

# 4. Review API costs in DeepSeek dashboard
# https://platform.deepseek.com/usage
```

---

## Success Checklist

Before going into production, verify:

- [ ] ✅ DeepSeek API key works (test call successful)
- [ ] ✅ Shadow trading runs manually without errors
- [ ] ✅ Logs are being generated correctly
- [ ] ✅ Cron/systemd timer is scheduled correctly
- [ ] ✅ Automated run completes successfully
- [ ] ✅ Cost tracking shows reasonable daily spend (<$5/day)
- [ ] ✅ LLM signals vary (not all NEUTRAL or all BULLISH)
- [ ] ✅ Can access logs remotely (if needed)
- [ ] ✅ Monitoring dashboard works (shadow_trading_status.sh)

---

## Timeline Summary

**Total Setup Time: 1-2 hours**

| Step | Time | Status |
|------|------|--------|
| OS Setup | 15-30 min | ⏸️ Pending |
| Python Install | 10 min | ⏸️ Pending |
| Project Clone | 5 min | ⏸️ Pending |
| API Config | 10 min | ⏸️ Pending |
| Testing | 15 min | ⏸️ Pending |
| Automation | 15 min | ⏸️ Pending |
| Monitoring | 10 min | ⏸️ Pending |

**After setup:** Machine runs autonomously, collecting shadow trading data daily.

---

## Next Steps After Setup

1. **Week 1-2:** Let shadow trading run daily, collect 20-30 decisions
2. **Week 3:** Generate accuracy report (`python shadow_trading.py --report`)
3. **Week 4:** Analyze results, decide on paper trading

**Decision Point:**
- If LLM accuracy >65% → Proceed to paper trading
- If 55-65% → Fine-tune prompt, continue shadow trading
- If <55% → Pause, re-evaluate approach

---

**Last Updated:** 2026-01-15
**Status:** Ready for deployment
**Support:** See troubleshooting section or review main README
