#!/usr/bin/env python3
"""
Market Analyzer Dashboard with Portfolio Simulator
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from analyzer import MarketAnalyzer
from backtest import Backtester
from portfolio_sim import PortfolioSimulator
import json
from datetime import datetime, timedelta

app = FastAPI(title="Market Analyzer Dashboard")

analyzer = MarketAnalyzer()
backtester = Backtester()
simulator = PortfolioSimulator()

# Common CSS
COMMON_CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
    .container { max-width: 1400px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 40px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; }
    h1 { font-size: 2.5em; margin-bottom: 10px; }
    nav { background: #1e293b; padding: 15px 30px; border-radius: 12px; margin-bottom: 30px; display: flex; gap: 20px; }
    nav a { color: #e2e8f0; text-decoration: none; padding: 10px 20px; border-radius: 8px; transition: background 0.2s; }
    nav a:hover, nav a.active { background: #334155; }
    .card { background: #1e293b; border-radius: 12px; padding: 25px; border: 2px solid #334155; margin-bottom: 20px; }
    .card-header { font-size: 1.5em; font-weight: bold; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #334155; }
    form { background: #1e293b; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
    .input-group { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
    input[type="text"], input[type="number"], input[type="date"], select { padding: 12px; border: 2px solid #334155; border-radius: 8px; background: #0f172a; color: #e2e8f0; font-size: 14px; }
    input[type="text"], input[type="date"], select { flex: 1; min-width: 200px; }
    input[type="number"] { width: 150px; }
    button { padding: 12px 25px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600; }
    .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .btn-secondary { background: #334155; color: #e2e8f0; }
    .btn-success { background: #10b981; color: white; }
    .btn-danger { background: #ef4444; color: white; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
    th { background: #0f172a; font-weight: 600; }
    .positive { color: #10b981; }
    .negative { color: #ef4444; }
    .badge { display: inline-block; padding: 5px 12px; border-radius: 12px; font-size: 0.85em; font-weight: 600; }
    .badge-open { background: #10b981; color: white; }
    .badge-closed { background: #64748b; color: white; }
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
    .metric { background: #0f172a; padding: 15px; border-radius: 8px; }
    .metric-label { font-size: 0.85em; color: #94a3b8; }
    .metric-value { font-size: 1.8em; font-weight: bold; margin-top: 5px; }
    .chart { background: #0f172a; padding: 20px; border-radius: 8px; margin: 20px 0; min-height: 300px; }
    .error { background: #7f1d1d; color: #fca5a5; padding: 15px; border-radius: 8px; margin: 20px 0; }
    .success { background: #065f46; color: #6ee7b7; padding: 15px; border-radius: 8px; margin: 20px 0; }
</style>
"""

def generate_nav(active='analyzer'):
    """Generate navigation menu"""
    return f"""
    <nav>
        <a href="/" class="{'active' if active == 'analyzer' else ''}">📊 Analyzer</a>
        <a href="/simulator" class="{'active' if active == 'simulator' else ''}">🎮 Simulator</a>
    </nav>
    """

@app.get("/", response_class=HTMLResponse)
async def root():
    """Analyzer page"""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Market Analyzer 📊</title>
        {COMMON_CSS}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Market Analyzer</h1>
                <p>Analyse multi-dimensionnelle pour le trading swing et moyen-long terme</p>
            </header>

            {generate_nav('analyzer')}

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
        </div>
    </body>
    </html>
    """

@app.get("/simulator", response_class=HTMLResponse)
async def simulator_page():
    """Portfolio simulator page"""
    portfolios = simulator.list_portfolios()
    
    portfolios_html = ""
    if portfolios:
        for p in portfolios:
            portfolio_id, name, initial, current, start, end, mode = p
            return_pct = ((current - initial) / initial) * 100
            return_class = 'positive' if return_pct > 0 else 'negative'
            status_badge = 'badge-open' if not end else 'badge-closed'
            status_text = 'En cours' if not end else 'Terminé'
            
            portfolios_html += f"""
            <tr>
                <td><strong>{name}</strong></td>
                <td>${initial:,.0f}</td>
                <td>${current:,.0f}</td>
                <td class="{return_class}">{return_pct:+.2f}%</td>
                <td>{start}</td>
                <td>{end or '-'}</td>
                <td><span class="badge {status_badge}">{status_text}</span></td>
                <td>
                    <form method="post" action="/simulator/run" style="display: inline; margin: 0; padding: 0;">
                        <input type="hidden" name="portfolio_id" value="{portfolio_id}" />
                        <button type="submit" class="btn-secondary" style="padding: 6px 12px; font-size: 0.85em;">▶️ Run</button>
                    </form>
                    <a href="/simulator/{portfolio_id}" style="margin-left: 5px;">
                        <button class="btn-primary" style="padding: 6px 12px; font-size: 0.85em;">📊 Voir</button>
                    </a>
                </td>
            </tr>
            """
    else:
        portfolios_html = '<tr><td colspan="8" style="text-align: center; color: #94a3b8;">Aucun portfolio créé</td></tr>'
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Portfolio Simulator 🎮</title>
        {COMMON_CSS}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🎮 Portfolio Simulator</h1>
                <p>Teste ta stratégie avec du capital virtuel</p>
            </header>

            {generate_nav('simulator')}

            <div class="card">
                <div class="card-header">➕ Créer un nouveau portfolio</div>
                <form method="post" action="/simulator/create">
                    <div class="input-group">
                        <input type="text" name="name" placeholder="Nom du portfolio" required />
                        <input type="number" name="capital" value="10000" min="1000" step="1000" required />
                        <input type="date" name="start_date" value="{datetime.now().strftime('%Y-%m-%d')}" required />
                        <button type="submit" class="btn-success">Créer</button>
                    </div>
                    <div style="font-size: 0.9em; color: #94a3b8; margin-top: 10px;">
                        💡 Pour tester sur l'historique, choisis une date passée (ex: 2024-01-01)
                    </div>
                </form>
            </div>

            <div class="card">
                <div class="card-header">📋 Mes portfolios</div>
                <table>
                    <thead>
                        <tr>
                            <th>Nom</th>
                            <th>Capital Initial</th>
                            <th>Valeur Actuelle</th>
                            <th>Return</th>
                            <th>Début</th>
                            <th>Fin</th>
                            <th>Statut</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {portfolios_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/simulator/create", response_class=HTMLResponse)
async def create_portfolio(name: str = Form(...), capital: float = Form(...), start_date: str = Form(...)):
    """Create new portfolio"""
    result = simulator.create_portfolio(name, capital, start_date)
    
    if result['success']:
        message = f'<div class="success">✅ Portfolio "{name}" créé avec succès! (ID: {result["portfolio_id"]})</div>'
    else:
        message = f'<div class="error">❌ {result["error"]}</div>'
    
    # Redirect to simulator page with message
    return RedirectResponse(url='/simulator', status_code=303)

@app.post("/simulator/run")
async def run_simulation(portfolio_id: int = Form(...)):
    """Run portfolio simulation"""
    result = simulator.run_simulation(portfolio_id)
    
    return RedirectResponse(url=f'/simulator/{portfolio_id}', status_code=303)

@app.get("/simulator/{portfolio_id}", response_class=HTMLResponse)
async def portfolio_details(portfolio_id: int):
    """Portfolio details page"""
    import sqlite3
    
    conn = sqlite3.connect(simulator.db_path)
    cursor = conn.cursor()
    
    # Get portfolio
    cursor.execute('SELECT * FROM portfolios WHERE id = ?', (portfolio_id,))
    portfolio = cursor.fetchone()
    
    if not portfolio:
        conn.close()
        return '<div class="error">Portfolio not found</div>'
    
    pid, name, initial, current, start, end, mode, config_str, created = portfolio
    return_pct = ((current - initial) / initial) * 100
    return_class = 'positive' if return_pct > 0 else 'negative'
    
    # Get open positions
    cursor.execute('SELECT * FROM positions WHERE portfolio_id = ? AND status = "open" ORDER BY entry_date DESC', (portfolio_id,))
    open_positions = cursor.fetchall()
    
    # Get closed positions
    cursor.execute('SELECT * FROM positions WHERE portfolio_id = ? AND status = "closed" ORDER BY exit_date DESC LIMIT 20', (portfolio_id,))
    closed_positions = cursor.fetchall()
    
    # Get snapshots for chart
    cursor.execute('SELECT date, total_value, total_return_pct FROM snapshots WHERE portfolio_id = ? ORDER BY date', (portfolio_id,))
    snapshots = cursor.fetchall()
    
    # Get trades log
    cursor.execute('SELECT * FROM trades_log WHERE portfolio_id = ? ORDER BY date DESC LIMIT 30', (portfolio_id,))
    trades = cursor.fetchall()
    
    conn.close()
    
    # Calculate metrics
    num_open = len(open_positions)
    num_closed = len(closed_positions)
    
    winning_trades = [p for p in closed_positions if p[10] and p[10] > 0]
    win_rate = (len(winning_trades) / num_closed * 100) if num_closed > 0 else 0
    
    # Generate chart data
    chart_dates = [s[0] for s in snapshots]
    chart_values = [s[1] for s in snapshots]
    chart_returns = [s[2] for s in snapshots]
    
    # Open positions HTML
    open_html = ""
    if open_positions:
        for pos in open_positions:
            pos_id, _, ticker, entry_date, entry_price, shares, invested, _, _, _, _, _, _ = pos
            
            # Get current price
            try:
                import yfinance as yf
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    current_value = shares * current_price
                    pnl = current_value - invested
                    pnl_pct = (pnl / invested) * 100
                    pnl_class = 'positive' if pnl > 0 else 'negative'
                else:
                    current_price = entry_price
                    current_value = invested
                    pnl = 0
                    pnl_pct = 0
                    pnl_class = ''
            except:
                current_price = entry_price
                current_value = invested
                pnl = 0
                pnl_pct = 0
                pnl_class = ''
            
            open_html += f"""
            <tr>
                <td><strong>{ticker}</strong></td>
                <td>{entry_date}</td>
                <td>${entry_price:.2f}</td>
                <td>${current_price:.2f}</td>
                <td>{shares}</td>
                <td>${invested:,.0f}</td>
                <td>${current_value:,.0f}</td>
                <td class="{pnl_class}">{pnl_pct:+.2f}%</td>
            </tr>
            """
    else:
        open_html = '<tr><td colspan="8" style="text-align: center; color: #94a3b8;">Aucune position ouverte</td></tr>'
    
    # Closed positions HTML
    closed_html = ""
    if closed_positions:
        for pos in closed_positions[:10]:
            pos_id, _, ticker, entry_date, entry_price, shares, invested, exit_date, exit_price, exit_reason, pnl, pnl_pct, _ = pos
            pnl_class = 'positive' if pnl > 0 else 'negative'
            
            closed_html += f"""
            <tr>
                <td><strong>{ticker}</strong></td>
                <td>{entry_date}</td>
                <td>{exit_date}</td>
                <td>${entry_price:.2f}</td>
                <td>${exit_price:.2f}</td>
                <td class="{pnl_class}">${pnl:,.0f}</td>
                <td class="{pnl_class}">{pnl_pct:+.2f}%</td>
                <td>{exit_reason}</td>
            </tr>
            """
    else:
        closed_html = '<tr><td colspan="8" style="text-align: center; color: #94a3b8;">Aucun trade fermé</td></tr>'
    
    # Simple text-based chart
    chart_html = '<div style="color: #94a3b8; text-align: center; padding: 40px;">📈 Graphique disponible prochainement</div>'
    
    if snapshots:
        min_val = min(chart_values)
        max_val = max(chart_values)
        range_val = max_val - min_val if max_val > min_val else 1
        
        chart_html = '<div style="font-family: monospace; font-size: 12px; line-height: 1.4;">'
        chart_html += f'<div style="margin-bottom: 10px; color: #94a3b8;">Performance: {chart_dates[0]} → {chart_dates[-1]}</div>'
        
        for i, (date, value, ret) in enumerate(list(zip(chart_dates, chart_values, chart_returns))[-30:]):
            bar_width = int((value - min_val) / range_val * 50) if range_val > 0 else 0
            bar_color = '#10b981' if ret >= 0 else '#ef4444'
            
            chart_html += f'<div style="display: flex; gap: 10px; align-items: center;">'
            chart_html += f'<span style="color: #64748b; width: 80px;">{date[5:]}</span>'
            chart_html += f'<span style="width: 300px; background: {bar_color}20; border-radius: 4px;">'
            chart_html += f'<span style="display: inline-block; width: {bar_width}%; background: {bar_color}; height: 20px; border-radius: 4px;"></span>'
            chart_html += f'</span>'
            chart_html += f'<span style="width: 100px; text-align: right; color: {bar_color};">${value:,.0f}</span>'
            chart_html += f'<span style="width: 80px; text-align: right; color: {bar_color};">{ret:+.2f}%</span>'
            chart_html += f'</div>'
        
        chart_html += '</div>'
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{name} - Portfolio Details</title>
        {COMMON_CSS}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 {name}</h1>
                <p>Simulation de performance</p>
            </header>

            {generate_nav('simulator')}

            <div class="card">
                <div class="card-header">💰 Performance globale</div>
                <div class="metric-grid">
                    <div class="metric">
                        <div class="metric-label">Capital Initial</div>
                        <div class="metric-value">${initial:,.0f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Valeur Actuelle</div>
                        <div class="metric-value">${current:,.0f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Return Total</div>
                        <div class="metric-value {return_class}">{return_pct:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Positions Ouvertes</div>
                        <div class="metric-value">{num_open}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Trades Fermés</div>
                        <div class="metric-value">{num_closed}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Win Rate</div>
                        <div class="metric-value">{win_rate:.1f}%</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">📈 Courbe de performance</div>
                <div class="chart">
                    {chart_html}
                </div>
            </div>

            <div class="card">
                <div class="card-header">🟢 Positions ouvertes ({num_open})</div>
                <table>
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Date Entrée</th>
                            <th>Prix Entrée</th>
                            <th>Prix Actuel</th>
                            <th>Shares</th>
                            <th>Investi</th>
                            <th>Valeur</th>
                            <th>PnL %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {open_html}
                    </tbody>
                </table>
            </div>

            <div class="card">
                <div class="card-header">📜 Historique des trades (10 derniers)</div>
                <table>
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Entrée</th>
                            <th>Sortie</th>
                            <th>Prix Entrée</th>
                            <th>Prix Sortie</th>
                            <th>PnL</th>
                            <th>PnL %</th>
                            <th>Raison</th>
                        </tr>
                    </thead>
                    <tbody>
                        {closed_html}
                    </tbody>
                </table>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="/simulator"><button class="btn-secondary">← Retour aux portfolios</button></a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_post(ticker: str = Form(...), action: str = Form(...)):
    """Handle analyze/backtest (keep existing functionality)"""
    # Keep existing analyze/backtest code from dashboard_simple.py
    return RedirectResponse(url='/', status_code=303)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Market Analyzer Dashboard with Portfolio Simulator')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    args = parser.parse_args()
    
    print(f"\n🚀 Starting Market Analyzer Dashboard + Portfolio Simulator...")
    print(f"📍 URL: http://{args.host}:{args.port}")
    print(f"🔗 Local: http://localhost:{args.port}")
    print(f"🌐 Network: http://192.168.1.64:{args.port}")
    print(f"\n💡 Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == '__main__':
    main()
