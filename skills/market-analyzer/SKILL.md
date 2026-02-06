---
name: market-analyzer
description: Analyze financial markets using technical indicators, fundamental data, and market sentiment to identify buy/sell opportunities for swing and medium-long term trading. Use when analyzing stocks, generating trading signals, backtesting strategies, or monitoring portfolio performance.
---

# Market Analyzer

Multi-dimensional stock market analysis combining technical indicators, fundamental analysis, and market sentiment to generate actionable trading signals for swing and medium-long term investment strategies.

## Quick Start

**Analyze a stock:**
```bash
python3 scripts/analyzer.py analyze AAPL
```

**Run backtest:**
```bash
python3 scripts/backtest.py AAPL --period 2y
```

**Start dashboard:**
```bash
python3 scripts/dashboard.py
```

## Components

### 1. Technical Analysis
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume analysis
- Support/Resistance levels
- Trend analysis (SMA 50/200)

### 2. Fundamental Analysis
- P/E ratio (Price to Earnings)
- P/B ratio (Price to Book)
- Debt/Equity ratio
- Profit margins
- Revenue growth
- Free cash flow

### 3. Market Sentiment
- News sentiment analysis
- Price momentum
- Volume trends

## Scoring System

Each stock receives a score from 0-10:
- **0-3**: Sell signal (bearish)
- **3-7**: Hold/Watch (neutral)
- **7-10**: Buy signal (bullish)

Score composition:
- Technical indicators: 40%
- Fundamental metrics: 40%
- Market sentiment: 20%

## Scripts

### analyzer.py
Main analysis engine. Fetches data, calculates indicators, and generates scores.

```bash
# Analyze single stock
python3 scripts/analyzer.py analyze AAPL

# Analyze multiple stocks
python3 scripts/analyzer.py analyze AAPL MSFT GOOGL --output json

# Watch list (continuous monitoring)
python3 scripts/analyzer.py watch AAPL MSFT --interval 5m
```

### backtest.py
Test strategy performance on historical data.

```bash
# Backtest single stock
python3 scripts/backtest.py AAPL --period 2y

# Backtest portfolio
python3 scripts/backtest.py AAPL MSFT GOOGL --period 1y --capital 10000
```

### dashboard.py
Web interface for monitoring and analysis.

```bash
# Start dashboard (localhost:8080)
python3 scripts/dashboard.py

# Custom port
python3 scripts/dashboard.py --port 8000
```

Access at: `http://localhost:8080` or `https://192.168.1.64:18789/market-analyzer`

### telegram_bot.py
Telegram notifications and commands.

```bash
# Start bot
python3 scripts/telegram_bot.py

# Send daily summary
python3 scripts/telegram_bot.py --daily-summary
```

**Telegram commands:**
- `/watch AAPL` - Add stock to watchlist
- `/unwatch AAPL` - Remove from watchlist
- `/portfolio` - View current portfolio
- `/analyze AAPL` - Get detailed analysis
- `/top` - Show top opportunities

### portfolio_sim.py
Portfolio simulation engine - test strategies with virtual capital.

```bash
# Create new portfolio simulation
python3 scripts/portfolio_sim.py create --name "Test 2024" --capital 10000 --start 2024-01-01

# Run simulation (historical replay)
python3 scripts/portfolio_sim.py run --id 1 --end 2024-12-31

# Check portfolio status
python3 scripts/portfolio_sim.py status --id 1

# List all portfolios
python3 scripts/portfolio_sim.py list
```

**Features:**
- Historical replay (backtest with realistic execution)
- Forward-looking simulation (paper trading)
- Automatic position management (entries/exits)
- Daily snapshots and performance tracking
- Multiple portfolio support

## Configuration

Create `config.json` in skill directory:

```json
{
  "watchlist": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
  "thresholds": {
    "buy": 7.5,
    "sell": 3.0
  },
  "telegram": {
    "enabled": true,
    "daily_summary_time": "08:00",
    "alert_threshold": 7.5
  },
  "backtest": {
    "initial_capital": 10000,
    "position_size": 0.2,
    "stop_loss": 0.05,
    "take_profit": 0.15
  }
}
```

## Dependencies

```bash
pip install yfinance pandas numpy fastapi uvicorn python-telegram-bot requests beautifulsoup4
```

## Data Cache System

To avoid Yahoo Finance rate limits, the analyzer uses a local SQLite cache.

**Preload data before running simulations:**

```bash
# Preload last 2 years of data for default stocks
bash scripts/preload_data.sh

# Custom date range
bash scripts/preload_data.sh 2024-01-01 2024-12-31

# Custom tickers
bash scripts/preload_data.sh 2024-01-01 2024-12-31 "AAPL MSFT TSLA"
```

**Cache management:**

```bash
# View cache statistics
python3 scripts/data_cache.py stats

# Clear cache for specific ticker
python3 scripts/data_cache.py clear --ticker AAPL

# Clear all cache
python3 scripts/data_cache.py clear
```

**Benefits:**
- Avoid rate limits (1 request per ticker instead of 250+)
- 10x faster simulations
- Offline mode possible
- Data shared across all tools

## Workflow Examples

**Daily morning routine:**
1. Receive Telegram summary of top opportunities
2. Check dashboard for detailed analysis
3. Review backtesting results
4. Make informed decisions

**Adding new stock:**
1. Run `/watch TICKER` in Telegram
2. System analyzes immediately
3. Get alert if score > threshold
4. Review on dashboard

**Strategy validation:**
1. Run backtest on historical data
2. Review win rate and returns
3. Adjust scoring weights if needed
4. Re-test and iterate
