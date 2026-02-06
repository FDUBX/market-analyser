#!/usr/bin/env python3
"""
Market Analyzer Dashboard - Simple version without JavaScript
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from analyzer import MarketAnalyzer
from backtest import Backtester

app = FastAPI(title="Market Analyzer Dashboard")

analyzer = MarketAnalyzer()
backtester = Backtester()

def generate_html(results=None, backtest_result=None, error=None):
    """Generate HTML with results"""
    
    results_html = ""
    
    if error:
        results_html = f'<div style="background: #7f1d1d; color: #fca5a5; padding: 15px; border-radius: 8px; margin: 20px 0;">❌ {error}</div>'
    
    if results:
        for data in results:
            if 'error' in data:
                results_html += f'<div style="background: #7f1d1d; color: #fca5a5; padding: 15px; border-radius: 8px; margin: 20px 0;">❌ {data["ticker"]}: {data["error"]}</div>'
                continue
            
            signal_colors = {
                'BUY': '#10b981',
                'SELL': '#ef4444',
                'HOLD': '#f59e0b'
            }
            signal_color = signal_colors.get(data['signal'], '#94a3b8')
            
            indicators_html = ""
            for key, value in data['indicators'].items():
                if value is not None:
                    indicators_html += f"""
                    <div style="background: #0f172a; padding: 12px; border-radius: 6px;">
                        <div style="font-size: 0.85em; color: #94a3b8;">{key.replace('_', ' ').upper()}</div>
                        <div style="font-size: 1.2em; font-weight: 600; color: #e2e8f0;">{value}</div>
                    </div>
                    """
            
            results_html += f"""
            <div style="background: #1e293b; border-radius: 12px; padding: 25px; border: 2px solid #334155; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #334155;">
                    <div style="font-size: 1.8em; font-weight: bold;">{data['ticker']}</div>
                    <div style="font-size: 1.5em; color: #10b981;">${data['current_price']}</div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.9em; color: rgba(255,255,255,0.8); margin-bottom: 5px;">Score Total</div>
                        <div style="font-size: 2em; font-weight: bold;">{data['scores']['total']}/10</div>
                    </div>
                    <div style="background: #0f172a; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.9em; color: #94a3b8; margin-bottom: 5px;">Technique</div>
                        <div style="font-size: 2em; font-weight: bold;">{data['scores']['technical']}/10</div>
                    </div>
                    <div style="background: #0f172a; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.9em; color: #94a3b8; margin-bottom: 5px;">Fondamental</div>
                        <div style="font-size: 2em; font-weight: bold;">{data['scores']['fundamental']}/10</div>
                    </div>
                    <div style="background: #0f172a; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.9em; color: #94a3b8; margin-bottom: 5px;">Sentiment</div>
                        <div style="font-size: 2em; font-weight: bold;">{data['scores']['sentiment']}/10</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <span style="display: inline-block; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 1.1em; background: {signal_color}; color: white;">
                        {data['signal']}
                    </span>
                </div>
                
                <div style="display: flex; gap: 20px; margin-top: 20px;">
                    <div style="flex: 1; background: #0f172a; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #94a3b8; margin-bottom: 5px;">🎯 Target</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: #10b981;">${data['targets']['target']}</div>
                    </div>
                    <div style="flex: 1; background: #0f172a; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #94a3b8; margin-bottom: 5px;">🛑 Stop Loss</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: #ef4444;">${data['targets']['stop_loss']}</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 20px;">
                    {indicators_html}
                </div>
            </div>
            """
    
    if backtest_result and 'error' not in backtest_result:
        data = backtest_result
        vs_class = 'positive' if data['vs_buy_hold'] > 0 else 'negative'
        vs_color = '#10b981' if data['vs_buy_hold'] > 0 else '#ef4444'
        
        trades_html = ""
        for trade in data['trades'][-10:][::-1]:
            pnl_color = '#10b981' if trade['pnl'] > 0 else '#ef4444'
            trades_html += f"""
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <span>{trade['entry_date']} → {trade['exit_date']}</span>
                    <span style="color: {pnl_color};">{'+' if trade['pnl_pct'] > 0 else ''}{trade['pnl_pct']}%</span>
                </div>
                <div style="font-size: 0.9em; color: #94a3b8; margin-top: 5px;">
                    ${trade['entry_price']} → ${trade['exit_price']} ({trade['reason']})
                </div>
            </div>
            """
        
        results_html += f"""
        <div style="background: #1e293b; border-radius: 12px; padding: 25px; border: 2px solid #334155;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #334155;">
                <div style="font-size: 1.8em; font-weight: bold;">📈 BACKTEST - {data['ticker']}</div>
                <div style="color: #94a3b8;">{data['period']}</div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="background: #0f172a; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 0.85em; color: #94a3b8;">Capital Initial</div>
                    <div style="font-size: 1.8em; font-weight: bold; margin-top: 5px;">${data['initial_capital']:,}</div>
                </div>
                <div style="background: #0f172a; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 0.85em; color: #94a3b8;">Capital Final</div>
                    <div style="font-size: 1.8em; font-weight: bold; margin-top: 5px;">${data['final_capital']:,}</div>
                </div>
                <div style="background: #0f172a; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 0.85em; color: #94a3b8;">Retour Total</div>
                    <div style="font-size: 1.8em; font-weight: bold; margin-top: 5px; color: {vs_color};">
                        {'+' if data['total_return_pct'] > 0 else ''}{data['total_return_pct']}%
                    </div>
                </div>
                <div style="background: #0f172a; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 0.85em; color: #94a3b8;">vs Buy & Hold</div>
                    <div style="font-size: 1.8em; font-weight: bold; margin-top: 5px; color: {vs_color};">
                        {'+' if data['vs_buy_hold'] > 0 else ''}{data['vs_buy_hold']}%
                    </div>
                </div>
                <div style="background: #0f172a; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 0.85em; color: #94a3b8;">Nombre Trades</div>
                    <div style="font-size: 1.8em; font-weight: bold; margin-top: 5px;">{data['num_trades']}</div>
                </div>
                <div style="background: #0f172a; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 0.85em; color: #94a3b8;">Win Rate</div>
                    <div style="font-size: 1.8em; font-weight: bold; margin-top: 5px;">{data['win_rate']}%</div>
                </div>
                <div style="background: #0f172a; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 0.85em; color: #94a3b8;">Avg Win</div>
                    <div style="font-size: 1.8em; font-weight: bold; margin-top: 5px; color: #10b981;">${data['avg_win']:,}</div>
                </div>
                <div style="background: #0f172a; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 0.85em; color: #94a3b8;">Avg Loss</div>
                    <div style="font-size: 1.8em; font-weight: bold; margin-top: 5px; color: #ef4444;">${data['avg_loss']:,}</div>
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <h3 style="margin-bottom: 15px;">Derniers trades</h3>
                {trades_html}
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Market Analyzer 📊</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            header {{ text-align: center; margin-bottom: 40px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; }}
            h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
            form {{ background: #1e293b; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
            .input-group {{ display: flex; gap: 10px; margin-bottom: 15px; }}
            input[type="text"] {{ flex: 1; padding: 15px; border: 2px solid #334155; border-radius: 8px; background: #0f172a; color: #e2e8f0; font-size: 16px; }}
            button {{ padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: 600; }}
            .btn-primary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
            .btn-secondary {{ background: #334155; color: #e2e8f0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Market Analyzer</h1>
                <p>Analyse multi-dimensionnelle pour le trading swing et moyen-long terme</p>
            </header>

            <form method="post" action="/analyze">
                <div class="input-group">
                    <input type="text" name="ticker" placeholder="Ticker (ex: AAPL, MSFT, GOOGL...)" required />
                    <button type="submit" name="action" value="analyze" class="btn-primary">Analyser</button>
                    <button type="submit" name="action" value="backtest" class="btn-secondary">Backtest</button>
                </div>
                <div style="font-size: 0.9em; color: #94a3b8;">
                    💡 Tip: Sépare plusieurs tickers par des espaces pour analyser plusieurs actions
                </div>
            </form>

            {results_html}
        </div>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve dashboard"""
    return generate_html()

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_post(ticker: str = Form(...), action: str = Form(...)):
    """Handle analyze/backtest form submission"""
    ticker = ticker.strip().upper()
    
    if action == "analyze":
        tickers = ticker.split()
        results = []
        for t in tickers:
            result = analyzer.analyze_stock(t)
            results.append(result)
        return generate_html(results=results)
    
    elif action == "backtest":
        result = backtester.backtest_stock(ticker.split()[0], "2y")
        return generate_html(backtest_result=result)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Market Analyzer Dashboard (Simple)')
    parser.add_argument('--port', type=int, default=8081, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    args = parser.parse_args()
    
    print(f"\n🚀 Starting Market Analyzer Dashboard (Simple Version)...")
    print(f"📍 URL: http://{args.host}:{args.port}")
    print(f"🔗 Local: http://localhost:{args.port}")
    print(f"🌐 Network: http://192.168.1.64:{args.port}")
    print(f"\n💡 Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == '__main__':
    main()
