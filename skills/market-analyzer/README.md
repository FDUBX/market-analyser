# Market Analyzer 📊

Stock market analysis tool combining technical indicators, fundamentals, and sentiment for swing/medium-long term trading.

## Quick Start

### 1. Install dependencies

```bash
bash scripts/install_deps.sh
```

Or manually:
```bash
pip install -r requirements.txt
```

### 2. Analyze a stock

```bash
python3 scripts/analyzer.py analyze AAPL
```

### 3. Run backtest

```bash
python3 scripts/backtest.py AAPL --period 2y
```

## Features

- ✅ Multi-dimensional analysis (Technical + Fundamental + Sentiment)
- ✅ 0-10 scoring system with clear BUY/SELL/HOLD signals  
- ✅ Backtesting engine with performance metrics
- 🚧 Web dashboard (coming soon)
- 🚧 Telegram notifications (coming soon)

## Example Output

```
📊 AAPL - $175.50
==================================================
Total Score: 7.8/10
  Technical:    8.2/10
  Fundamental:  7.5/10
  Sentiment:    7.6/10

Signal: BUY
Target: $195.00
Stop Loss: $168.00

Key Indicators:
  rsi: 32.5
  pe_ratio: 24.3
  profit_margin: 25.8%
```

## Documentation

See `SKILL.md` for detailed usage and configuration.
