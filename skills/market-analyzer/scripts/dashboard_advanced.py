#!/usr/bin/env python3
"""
Advanced Market Analyzer Dashboard with Chart.js and Strategy Comparison
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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

# Load strategies
import os
strategies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'strategies.json')
with open(strategies_path, 'r') as f:
    STRATEGIES = json.load(f)

# Common CSS + Chart.js
COMMON_HEAD = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
    .container { max-width: 1400px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 40px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; }
    h1 { font-size: 2.5em; margin-bottom: 10px; }
    nav { background: #1e293b; padding: 15px 30px; border-radius: 12px; margin-bottom: 30px; display: flex; gap: 20px; flex-wrap: wrap; }
    nav a { color: #e2e8f0; text-decoration: none; padding: 10px 20px; border-radius: 8px; transition: background 0.2s; }
    nav a:hover, nav a.active { background: #334155; }
    .card { background: #1e293b; border-radius: 12px; padding: 25px; border: 2px solid #334155; margin-bottom: 20px; }
    .card-header { font-size: 1.5em; font-weight: bold; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #334155; }
    form { background: #1e293b; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
    .input-group { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
    input, select { padding: 12px; border: 2px solid #334155; border-radius: 8px; background: #0f172a; color: #e2e8f0; font-size: 14px; }
    input, select { flex: 1; min-width: 200px; }
    button { padding: 12px 25px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600; }
    .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .btn-secondary { background: #334155; color: #e2e8f0; }
    .btn-success { background: #10b981; color: white; }
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
    .chart-container { position: relative; height: 400px; margin: 20px 0; }
    .strategy-card { background: #0f172a; padding: 15px; border-radius: 8px; margin-bottom: 10px; border: 2px solid #334155; transition: border-color 0.2s; }
    .strategy-card:hover { border-color: #667eea; }
    .strategy-card.selected { border-color: #10b981; background: #065f4620; }
</style>
"""

def generate_nav(active='simulator'):
    return f"""
    <nav>
        <a href="/" class="{'active' if active == 'analyzer' else ''}">📊 Analyzer</a>
        <a href="/simulator" class="{'active' if active == 'simulator' else ''}">🎮 Simulator</a>
        <a href="/strategies" class="{'active' if active == 'strategies' else ''}">⚙️ Strategies</a>
        <a href="/compare" class="{'active' if active == 'compare' else ''}">📈 Compare</a>
    </nav>
    """

@app.get("/", response_class=HTMLResponse)
async def root():
    """Analyzer page"""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>Market Analyzer 📊</title>
        {COMMON_HEAD}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Market Analyzer</h1>
                <p>Analyse multi-dimensionnelle avancée</p>
            </header>
            {generate_nav('analyzer')}
            <div class="card">
                <div class="card-header">Analyse d'actions</div>
                <form method="post" action="/api/analyze">
                    <div class="input-group">
                        <input type="text" name="ticker" placeholder="Ticker (AAPL, MSFT...)" required />
                        <button type="submit" class="btn-primary">Analyser</button>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/strategies", response_class=HTMLResponse)
async def strategies_page():
    """Strategies comparison page"""
    
    strategies_html = ""
    for name, config in STRATEGIES.items():
        strategies_html += f"""
        <div class="strategy-card">
            <h3 style="margin-bottom: 10px;">{name}</h3>
            <p style="color: #94a3b8; margin-bottom: 15px;">{config['description']}</p>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; font-size: 0.9em;">
                <div><strong>BUY:</strong> {config['buy_threshold']}</div>
                <div><strong>SELL:</strong> {config['sell_threshold']}</div>
                <div><strong>Position:</strong> {config['position_size']:.0%}</div>
                <div><strong>Stop-loss:</strong> {config['stop_loss']:.0%}</div>
                <div><strong>Take-profit:</strong> {config['take_profit']:.0%}</div>
                <div style="grid-column: 1/-1;"><strong>Weights:</strong> Tech {config['weights']['technical']:.0%} | Fund {config['weights']['fundamental']:.0%} | Sent {config['weights']['sentiment']:.0%}</div>
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>Strategies 🎯</title>
        {COMMON_HEAD}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>⚙️ Stratégies de Trading</h1>
                <p>5 stratégies pré-configurées à tester</p>
            </header>
            {generate_nav('strategies')}
            <div class="card">
                <div class="card-header">📚 Stratégies disponibles</div>
                {strategies_html}
            </div>
            <div class="card">
                <div class="card-header">🧪 Tester une stratégie</div>
                <form method="post" action="/simulator/create-with-strategy">
                    <div class="input-group">
                        <input type="text" name="name" placeholder="Nom du portfolio" required />
                        <select name="strategy" required>
                            <option value="">Choisir une stratégie...</option>
                            {"".join([f'<option value="{name}">{name}</option>' for name in STRATEGIES.keys()])}
                        </select>
                        <input type="number" name="capital" value="10000" min="1000" step="1000" required />
                        <input type="date" name="start_date" value="{datetime.now().strftime('%Y-%m-%d')}" required />
                        <button type="submit" class="btn-success">Créer avec stratégie</button>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/simulator/create-with-strategy")
async def create_with_strategy(
    name: str = Form(...),
    strategy: str = Form(...),
    capital: float = Form(...),
    start_date: str = Form(...)
):
    """Create portfolio with predefined strategy"""
    if strategy not in STRATEGIES:
        return RedirectResponse(url='/strategies', status_code=303)
    
    config = STRATEGIES[strategy]
    result = simulator.create_portfolio(name, capital, start_date, config=config)
    
    return RedirectResponse(url='/simulator', status_code=303)

@app.get("/simulator", response_class=HTMLResponse)
async def simulator_page():
    """Portfolio simulator (reuse existing)"""
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
                    <a href="/simulator/{portfolio_id}">
                        <button class="btn-primary" style="padding: 6px 12px; font-size: 0.85em; margin-left: 5px;">📊 Voir</button>
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
        <title>Portfolio Simulator 🎮</title>
        {COMMON_HEAD}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🎮 Portfolio Simulator</h1>
                <p>Teste ta stratégie avec du capital virtuel</p>
            </header>
            {generate_nav('simulator')}
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

@app.post("/simulator/run")
async def run_simulation(portfolio_id: int = Form(...)):
    """Run portfolio simulation"""
    result = simulator.run_simulation(portfolio_id)
    return RedirectResponse(url=f'/simulator/{portfolio_id}', status_code=303)

@app.get("/simulator/{portfolio_id}", response_class=HTMLResponse)
async def portfolio_details(portfolio_id: int):
    """Portfolio details with Chart.js"""
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
    
    # Get snapshots for chart
    cursor.execute('SELECT date, total_value, total_return_pct FROM snapshots WHERE portfolio_id = ? ORDER BY date', (portfolio_id,))
    snapshots = cursor.fetchall()
    
    conn.close()
    
    # Prepare Chart.js data
    chart_dates = [s[0] for s in snapshots]
    chart_values = [s[1] for s in snapshots]
    chart_returns = [s[2] for s in snapshots]
    
    chart_data_json = json.dumps({
        'labels': chart_dates,
        'values': chart_values,
        'returns': chart_returns,
        'initial': initial
    })
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>{name} - Details</title>
        {COMMON_HEAD}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 {name}</h1>
                <p>Performance détaillée</p>
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
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">📈 Courbe de performance</div>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="/simulator"><button class="btn-secondary">← Retour</button></a>
            </div>
        </div>
        
        <script>
            const chartData = {chart_data_json};
            const ctx = document.getElementById('performanceChart');
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: chartData.labels,
                    datasets: [{{
                        label: 'Valeur du portfolio',
                        data: chartData.values,
                        borderColor: '#667eea',
                        backgroundColor: '#667eea20',
                        fill: true,
                        tension: 0.4
                    }}, {{
                        label: 'Capital initial',
                        data: Array(chartData.labels.length).fill(chartData.initial),
                        borderColor: '#94a3b8',
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#e2e8f0' }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{ color: '#94a3b8' }},
                            grid: {{ color: '#334155' }}
                        }},
                        y: {{
                            ticks: {{ 
                                color: '#94a3b8',
                                callback: function(value) {{
                                    return '$' + value.toLocaleString();
                                }}
                            }},
                            grid: {{ color: '#334155' }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--host', default='0.0.0.0')
    args = parser.parse_args()
    
    print(f"\n🚀 Starting Advanced Market Analyzer Dashboard...")
    print(f"📍 http://192.168.1.64:{args.port}")
    print(f"\n💡 Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == '__main__':
    main()
