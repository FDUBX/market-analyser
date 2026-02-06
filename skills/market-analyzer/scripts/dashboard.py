#!/usr/bin/env python3
"""
Market Analyzer Dashboard - Web interface
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from datetime import datetime
from analyzer import MarketAnalyzer
from backtest import Backtester

app = FastAPI(title="Market Analyzer Dashboard")

# Initialize analyzer
analyzer = MarketAnalyzer()
backtester = Backtester()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Analyzer 📊</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .search-box {
            background: #1e293b;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #334155;
            border-radius: 8px;
            background: #0f172a;
            color: #e2e8f0;
            font-size: 16px;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-secondary {
            background: #334155;
            color: #e2e8f0;
        }
        .results {
            display: grid;
            gap: 20px;
        }
        .card {
            background: #1e293b;
            border-radius: 12px;
            padding: 25px;
            border: 2px solid #334155;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #334155;
        }
        .ticker {
            font-size: 1.8em;
            font-weight: bold;
        }
        .price {
            font-size: 1.5em;
            color: #10b981;
        }
        .score-display {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .score-item {
            background: #0f172a;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .score-label {
            font-size: 0.9em;
            color: #94a3b8;
            margin-bottom: 5px;
        }
        .score-value {
            font-size: 2em;
            font-weight: bold;
        }
        .score-total {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .signal {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1em;
        }
        .signal-buy {
            background: #10b981;
            color: white;
        }
        .signal-hold {
            background: #f59e0b;
            color: white;
        }
        .signal-sell {
            background: #ef4444;
            color: white;
        }
        .indicators {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }
        .indicator {
            background: #0f172a;
            padding: 12px;
            border-radius: 6px;
        }
        .indicator-label {
            font-size: 0.85em;
            color: #94a3b8;
        }
        .indicator-value {
            font-size: 1.2em;
            font-weight: 600;
            color: #e2e8f0;
        }
        .targets {
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }
        .target {
            flex: 1;
            background: #0f172a;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .target-label {
            color: #94a3b8;
            margin-bottom: 5px;
        }
        .target-value {
            font-size: 1.5em;
            font-weight: bold;
        }
        .target-up {
            color: #10b981;
        }
        .target-down {
            color: #ef4444;
        }
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
            color: #94a3b8;
        }
        .error {
            background: #7f1d1d;
            color: #fca5a5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .backtest-results {
            margin-top: 30px;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .metric {
            background: #0f172a;
            padding: 15px;
            border-radius: 8px;
        }
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            margin-top: 5px;
        }
        .positive {
            color: #10b981;
        }
        .negative {
            color: #ef4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Market Analyzer</h1>
            <p>Analyse multi-dimensionnelle pour le trading swing et moyen-long terme</p>
        </header>

        <div class="search-box">
            <div class="input-group">
                <input type="text" id="ticker" placeholder="Ticker (ex: AAPL, MSFT, GOOGL...)" />
                <button class="btn-primary" onclick="analyzeStock()">Analyser</button>
                <button class="btn-secondary" onclick="runBacktest()">Backtest</button>
            </div>
            <div style="font-size: 0.9em; color: #94a3b8; margin-top: 10px;">
                💡 Tip: Sépare plusieurs tickers par des espaces pour analyser plusieurs actions
            </div>
        </div>

        <div id="results" class="results"></div>
    </div>

    <script>
        async function analyzeStock() {
            const ticker = document.getElementById('ticker').value.trim().toUpperCase();
            if (!ticker) {
                alert('Entre un ticker (ex: AAPL)');
                return;
            }

            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading">⏳ Analyse en cours...</div>';

            try {
                const tickers = ticker.split(/[,\\s]+/);
                const results = [];
                
                for (const t of tickers) {
                    const response = await fetch(\`/api/analyze/\${t}\`);
                    const data = await response.json();
                    results.push(data);
                }

                displayResults(results);
            } catch (error) {
                resultsDiv.innerHTML = \`<div class="error">❌ Erreur: \${error.message}</div>\`;
            }
        }

        async function runBacktest() {
            const ticker = document.getElementById('ticker').value.trim().toUpperCase();
            if (!ticker) {
                alert('Entre un ticker (ex: AAPL)');
                return;
            }

            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading">⏳ Backtesting en cours (peut prendre 1-2 minutes)...</div>';

            try {
                const response = await fetch(\`/api/backtest/\${ticker}\`);
                const data = await response.json();
                displayBacktestResults(data);
            } catch (error) {
                resultsDiv.innerHTML = \`<div class="error">❌ Erreur: \${error.message}</div>\`;
            }
        }

        function displayResults(results) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';

            results.forEach(data => {
                if (data.error) {
                    resultsDiv.innerHTML += \`<div class="error">❌ \${data.ticker}: \${data.error}</div>\`;
                    return;
                }

                const signalClass = data.signal === 'BUY' ? 'signal-buy' : 
                                   data.signal === 'SELL' ? 'signal-sell' : 'signal-hold';
                
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = \`
                    <div class="card-header">
                        <div class="ticker">\${data.ticker}</div>
                        <div class="price">$\${data.current_price}</div>
                    </div>

                    <div class="score-display">
                        <div class="score-item score-total">
                            <div class="score-label">Score Total</div>
                            <div class="score-value">\${data.scores.total}/10</div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">Technique</div>
                            <div class="score-value">\${data.scores.technical}/10</div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">Fondamental</div>
                            <div class="score-value">\${data.scores.fundamental}/10</div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">Sentiment</div>
                            <div class="score-value">\${data.scores.sentiment}/10</div>
                        </div>
                    </div>

                    <div style="text-align: center; margin: 20px 0;">
                        <span class="signal \${signalClass}">\${data.signal}</span>
                    </div>

                    <div class="targets">
                        <div class="target">
                            <div class="target-label">🎯 Target</div>
                            <div class="target-value target-up">$\${data.targets.target}</div>
                        </div>
                        <div class="target">
                            <div class="target-label">🛑 Stop Loss</div>
                            <div class="target-value target-down">$\${data.targets.stop_loss}</div>
                        </div>
                    </div>

                    <div class="indicators">
                        \${Object.entries(data.indicators).map(([key, value]) => 
                            value !== null ? \`
                            <div class="indicator">
                                <div class="indicator-label">\${key.replace('_', ' ').toUpperCase()}</div>
                                <div class="indicator-value">\${value}</div>
                            </div>
                            \` : ''
                        ).join('')}
                    </div>
                \`;
                resultsDiv.appendChild(card);
            });
        }

        function displayBacktestResults(data) {
            const resultsDiv = document.getElementById('results');
            
            if (data.error) {
                resultsDiv.innerHTML = \`<div class="error">❌ \${data.error}</div>\`;
                return;
            }

            const vsClass = data.vs_buy_hold > 0 ? 'positive' : 'negative';
            
            resultsDiv.innerHTML = \`
                <div class="card">
                    <div class="card-header">
                        <div class="ticker">📈 BACKTEST - \${data.ticker}</div>
                        <div style="color: #94a3b8;">\${data.period}</div>
                    </div>

                    <div class="metric-grid">
                        <div class="metric">
                            <div class="indicator-label">Capital Initial</div>
                            <div class="metric-value">$\${data.initial_capital.toLocaleString()}</div>
                        </div>
                        <div class="metric">
                            <div class="indicator-label">Capital Final</div>
                            <div class="metric-value">$\${data.final_capital.toLocaleString()}</div>
                        </div>
                        <div class="metric">
                            <div class="indicator-label">Retour Total</div>
                            <div class="metric-value \${data.total_return > 0 ? 'positive' : 'negative'}">
                                \${data.total_return_pct > 0 ? '+' : ''}\${data.total_return_pct}%
                            </div>
                        </div>
                        <div class="metric">
                            <div class="indicator-label">vs Buy & Hold</div>
                            <div class="metric-value \${vsClass}">
                                \${data.vs_buy_hold > 0 ? '+' : ''}\${data.vs_buy_hold}%
                            </div>
                        </div>
                        <div class="metric">
                            <div class="indicator-label">Nombre Trades</div>
                            <div class="metric-value">\${data.num_trades}</div>
                        </div>
                        <div class="metric">
                            <div class="indicator-label">Win Rate</div>
                            <div class="metric-value">\${data.win_rate}%</div>
                        </div>
                        <div class="metric">
                            <div class="indicator-label">Avg Win</div>
                            <div class="metric-value positive">$\${data.avg_win.toLocaleString()}</div>
                        </div>
                        <div class="metric">
                            <div class="indicator-label">Avg Loss</div>
                            <div class="metric-value negative">$\${data.avg_loss.toLocaleString()}</div>
                        </div>
                    </div>

                    <div class="backtest-results">
                        <h3 style="margin-bottom: 15px;">Derniers trades</h3>
                        \${data.trades.slice(-10).reverse().map(trade => \`
                            <div class="indicator" style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between;">
                                    <span>\${trade.entry_date} → \${trade.exit_date}</span>
                                    <span class="\${trade.pnl > 0 ? 'positive' : 'negative'}">
                                        \${trade.pnl_pct > 0 ? '+' : ''}\${trade.pnl_pct}%
                                    </span>
                                </div>
                                <div style="font-size: 0.9em; color: #94a3b8; margin-top: 5px;">
                                    $\${trade.entry_price} → $\${trade.exit_price} (\${trade.reason})
                                </div>
                            </div>
                        \`).join('')}
                    </div>
                </div>
            \`;
        }

        // Enter key support
        document.getElementById('ticker').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeStock();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve dashboard HTML"""
    return HTML_TEMPLATE

@app.get("/api/analyze/{ticker}")
async def analyze(ticker: str):
    """Analyze a stock"""
    result = analyzer.analyze_stock(ticker.upper())
    return result

@app.get("/api/backtest/{ticker}")
async def backtest(ticker: str, period: str = "2y"):
    """Run backtest on a stock"""
    result = backtester.backtest_stock(ticker.upper(), period)
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Market Analyzer Dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    args = parser.parse_args()
    
    print(f"\n🚀 Starting Market Analyzer Dashboard...")
    print(f"📍 URL: http://{args.host}:{args.port}")
    print(f"🔗 Local: http://localhost:{args.port}")
    print(f"🌐 Network: https://192.168.1.64:18789/market-analyzer (via reverse proxy)")
    print(f"\n💡 Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == '__main__':
    main()
