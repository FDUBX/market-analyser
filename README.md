# OpenClaw Workspace - Market Analyzer 🦎

Personal AI assistant workspace with an optimized stock market analyzer.

## 🚀 Market Analyzer

Multi-dimensional stock analysis and portfolio simulation with **+21.65% average annual return** (validated on 2024-2025).

### Features

- **Technical Analysis** (RSI, MACD, Bollinger Bands, Volume, SMA)
- **Fundamental Analysis** (P/E, P/B, Margins, Debt, Growth)
- **Sentiment Analysis** (Price momentum, Volume trends)
- **Portfolio Simulator** (Backtest strategies with virtual capital)
- **Data Cache** (Local SQLite cache to avoid API rate limits)
- **Web Dashboard** (Chart.js interactive UI)

### Optimized Configuration

**Strategy:** Balanced Optimized

```json
{
  "buy_threshold": 5.3,
  "sell_threshold": 4.3,
  "stop_loss": 0.05,
  "take_profit": 0.18,
  "weights": {
    "technical": 0.4,
    "fundamental": 0.4,
    "sentiment": 0.2
  }
}
```

**Performance:**
- 2024 (bull market): **+32.47%**
- 2025 (mixed market): **+10.83%**
- **Average: +21.65% annual return**

### Quick Start

```bash
cd skills/market-analyzer

# Install dependencies
bash scripts/install_deps.sh

# Preload data (once)
bash scripts/preload_data.sh

# Launch dashboard
python3 scripts/dashboard_advanced.py --port 8080
```

Open http://localhost:8080

### Documentation

- **[INDEX.md](skills/market-analyzer/INDEX.md)** - Documentation index
- **[OPTIMIZATION_RESULTS.md](skills/market-analyzer/OPTIMIZATION_RESULTS.md)** - Optimization results ⭐
- **[QUICKSTART.md](skills/market-analyzer/QUICKSTART.md)** - Quick start guide
- **[README_COMPLETE.md](skills/market-analyzer/README_COMPLETE.md)** - Complete guide

## 📧 Email Management

IMAP email reader with ProtonMail Bridge support.

See [skills/imap-email/SKILL.md](skills/imap-email/SKILL.md)

## 🔧 Setup

**Requirements:**
- Python 3.8+
- Node.js 16+ (for email skills)
- OpenClaw (https://openclaw.ai)

**Environment:**
Create `.env` files in skill directories with your credentials (see `.env.example` files).

## 📝 License

Personal workspace - Not licensed for public use.

## 🦎 About

Built with [OpenClaw](https://openclaw.ai) - AI assistant framework.

Optimized by Molty 🦎
