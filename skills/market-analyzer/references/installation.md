# Installation Guide

## Quick Start (Automated)

```bash
bash scripts/install_deps.sh
```

## Manual Installation

### 1. Install pip (if not available)

```bash
sudo apt-get update
sudo apt-get install -y python3-pip
```

### 2. Install Python dependencies

```bash
python3 -m pip install --break-system-packages \
    yfinance \
    pandas \
    numpy \
    fastapi \
    uvicorn \
    requests \
    beautifulsoup4 \
    python-telegram-bot
```

### 3. Test the installation

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
python3 scripts/analyzer.py analyze AAPL
```

## System Package Alternative

If pip is not available, you can try installing via system packages:

```bash
sudo apt-get install -y \
    python3-pandas \
    python3-numpy \
    python3-requests \
    python3-bs4
```

Note: yfinance and fastapi may not be available as system packages and require pip.

## Troubleshooting

**"No module named pip":**
```bash
sudo apt-get install python3-pip
```

**Permission errors:**
Add `--break-system-packages` flag or use `--user` flag

**Import errors:**
Verify installation with:
```bash
python3 -c "import yfinance, pandas, numpy; print('OK')"
```
