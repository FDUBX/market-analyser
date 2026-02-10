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
        <a href="/live" class="{'active' if active == 'live' else ''}">🔴 Live Trading</a>
        <a href="/settings/telegram" class="{'active' if active == 'telegram' else ''}">✈️ Telegram</a>
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
                <form method="post" action="/analyze">
                    <div class="input-group">
                        <input type="text" name="ticker" placeholder="Ticker (AAPL, MSFT...)" required />
                        <button type="submit" class="btn-primary">Analyser</button>
                    </div>
                </form>
                <div id="result"></div>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/analyze")
async def analyze_stock(ticker: str = Form(...)):
    """Analyze a stock and display results"""
    try:
        result = analyzer.analyze_stock(ticker.upper())
        
        score = result['scores']['total']
        signal = result['signal']
        signal_color = '#10b981' if signal == 'BUY' else '#ef4444' if signal == 'SELL' else '#94a3b8'
        
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <title>{ticker.upper()} - Analyse</title>
            {COMMON_HEAD}
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>📊 {ticker.upper()} - ${result.get('price', 'N/A')}</h1>
                    <p>Analyse complète</p>
                </header>
                {generate_nav('analyzer')}
                
                <div class="card">
                    <div class="card-header">Score Global</div>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-label">Score Total</div>
                            <div class="metric-value">{score:.2f}/10</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Signal</div>
                            <div class="metric-value" style="color: {signal_color};">{signal}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Technique</div>
                            <div class="metric-value">{result['scores']['technical']:.2f}/10</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Fondamental</div>
                            <div class="metric-value">{result['scores']['fundamental']:.2f}/10</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Sentiment</div>
                            <div class="metric-value">{result['scores']['sentiment']:.2f}/10</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">Indicateurs Clés</div>
                    <table>
                        <tr><th>Indicateur</th><th>Valeur</th></tr>
                        <tr><td>RSI</td><td>{result.get('indicators', {}).get('rsi', 'N/A')}</td></tr>
                        <tr><td>P/E Ratio</td><td>{result.get('indicators', {}).get('pe_ratio', 'N/A')}</td></tr>
                        <tr><td>P/B Ratio</td><td>{result.get('indicators', {}).get('pb_ratio', 'N/A')}</td></tr>
                        <tr><td>Profit Margin</td><td>{result.get('indicators', {}).get('profit_margin', 'N/A')}</td></tr>
                        <tr><td>Revenue Growth</td><td>{result.get('indicators', {}).get('revenue_growth', 'N/A')}</td></tr>
                    </table>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/"><button class="btn-secondary">← Nouvelle analyse</button></a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(html)
        
    except Exception as e:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <title>Erreur</title>
            {COMMON_HEAD}
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>❌ Erreur</h1>
                </header>
                {generate_nav('analyzer')}
                <div class="card">
                    <div class="card-header">Erreur d'analyse</div>
                    <p style="color: #ef4444;">Impossible d'analyser {ticker.upper()}: {str(e)}</p>
                    <div style="margin-top: 20px;">
                        <a href="/"><button class="btn-primary">← Retour</button></a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """)

@app.get("/strategies", response_class=HTMLResponse)
async def strategies_page():
    """Strategies comparison page"""
    
    strategies_html = ""
    for name, config in STRATEGIES.items():
        strategies_html += f"""
        <div class="strategy-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                <h3 style="margin: 0;">{name}</h3>
                <a href="/strategies/edit/{name}"><button class="btn-secondary" style="padding: 6px 12px; font-size: 0.85em;">✏️ Éditer</button></a>
            </div>
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
                        <input type="date" name="end_date" placeholder="Date de fin (optionnelle)" />
                        <button type="submit" class="btn-success">Créer avec stratégie</button>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/strategies/edit/{strategy_name}", response_class=HTMLResponse)
async def edit_strategy(strategy_name: str):
    """Edit strategy page"""
    if strategy_name not in STRATEGIES:
        return RedirectResponse(url='/strategies', status_code=303)
    
    config = STRATEGIES[strategy_name]
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>Éditer {strategy_name}</title>
        {COMMON_HEAD}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>✏️ Éditer: {strategy_name}</h1>
                <p>Modifier les paramètres de la stratégie</p>
            </header>
            {generate_nav('strategies')}
            
            <div class="card">
                <div class="card-header">Paramètres</div>
                <form method="post" action="/strategies/save/{strategy_name}">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 5px; color: #94a3b8;">Description</label>
                        <input type="text" name="description" value="{config['description']}" required style="width: 100%;" />
                    </div>
                    
                    <div class="card-header" style="font-size: 1.2em; margin-top: 30px;">Seuils</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                        <div>
                            <label style="display: block; margin-bottom: 5px; color: #94a3b8;">BUY Threshold</label>
                            <input type="number" name="buy_threshold" value="{config['buy_threshold']}" step="0.1" min="0" max="10" required />
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; color: #94a3b8;">SELL Threshold</label>
                            <input type="number" name="sell_threshold" value="{config['sell_threshold']}" step="0.1" min="0" max="10" required />
                        </div>
                    </div>
                    
                    <div class="card-header" style="font-size: 1.2em; margin-top: 30px;">Gestion du Risque</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                        <div>
                            <label style="display: block; margin-bottom: 5px; color: #94a3b8;">Position Size (%)</label>
                            <input type="number" name="position_size" value="{config['position_size']*100}" step="1" min="1" max="100" required />
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; color: #94a3b8;">Stop-loss (%)</label>
                            <input type="number" name="stop_loss" value="{config['stop_loss']*100}" step="1" min="1" max="20" required />
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; color: #94a3b8;">Take-profit (%)</label>
                            <input type="number" name="take_profit" value="{config['take_profit']*100}" step="1" min="1" max="50" required />
                        </div>
                    </div>
                    
                    <div class="card-header" style="font-size: 1.2em; margin-top: 30px;">Pondérations</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                        <div>
                            <label style="display: block; margin-bottom: 5px; color: #94a3b8;">Technique (%)</label>
                            <input type="number" name="weight_technical" value="{config['weights']['technical']*100}" step="1" min="0" max="100" required />
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; color: #94a3b8;">Fondamental (%)</label>
                            <input type="number" name="weight_fundamental" value="{config['weights']['fundamental']*100}" step="1" min="0" max="100" required />
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; color: #94a3b8;">Sentiment (%)</label>
                            <input type="number" name="weight_sentiment" value="{config['weights']['sentiment']*100}" step="1" min="0" max="100" required />
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; display: flex; gap: 10px; justify-content: center;">
                        <button type="submit" class="btn-success">💾 Sauvegarder</button>
                        <a href="/strategies"><button type="button" class="btn-secondary">← Annuler</button></a>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/strategies/save/{strategy_name}")
async def save_strategy(
    strategy_name: str,
    description: str = Form(...),
    buy_threshold: float = Form(...),
    sell_threshold: float = Form(...),
    position_size: float = Form(...),
    stop_loss: float = Form(...),
    take_profit: float = Form(...),
    weight_technical: float = Form(...),
    weight_fundamental: float = Form(...),
    weight_sentiment: float = Form(...)
):
    """Save strategy modifications"""
    
    # Update strategy in memory
    STRATEGIES[strategy_name] = {
        'description': description,
        'buy_threshold': buy_threshold,
        'sell_threshold': sell_threshold,
        'position_size': position_size / 100,
        'stop_loss': stop_loss / 100,
        'take_profit': take_profit / 100,
        'weights': {
            'technical': weight_technical / 100,
            'fundamental': weight_fundamental / 100,
            'sentiment': weight_sentiment / 100
        }
    }
    
    # Save to file
    import os
    strategies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'strategies.json')
    with open(strategies_path, 'w') as f:
        json.dump(STRATEGIES, f, indent=2)
    
    return RedirectResponse(url='/strategies', status_code=303)

@app.post("/simulator/create-with-strategy")
async def create_with_strategy(
    name: str = Form(...),
    strategy: str = Form(...),
    capital: float = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(None)
):
    """Create portfolio with predefined strategy"""
    if strategy not in STRATEGIES:
        return RedirectResponse(url='/strategies', status_code=303)
    
    config = STRATEGIES[strategy]
    result = simulator.create_portfolio(name, capital, start_date, config=config)
    portfolio_id = result['portfolio_id']
    
    # Run simulation with end_date if provided
    simulator.run_simulation(portfolio_id, end_date=end_date if end_date else None)
    
    return RedirectResponse(url=f'/simulator/{portfolio_id}', status_code=303)

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
                    <form method="post" action="/simulator/delete/{portfolio_id}" style="display: inline; margin: 0; padding: 0; margin-left: 5px;" onsubmit="return confirm('Supprimer ce portfolio ?');">
                        <button type="submit" class="btn-secondary" style="padding: 6px 12px; font-size: 0.85em; background: #ef4444;">🗑️</button>
                    </form>
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
                <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <span>📋 Mes portfolios</span>
                    <form method="post" action="/simulator/delete-all" style="margin: 0;" onsubmit="return confirm('Supprimer TOUS les portfolios ? Cette action est irréversible.');">
                        <button type="submit" class="btn-secondary" style="padding: 8px 16px; font-size: 0.9em; background: #ef4444;">🗑️ Supprimer tout</button>
                    </form>
                </div>
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

@app.post("/simulator/delete/{portfolio_id}")
async def delete_portfolio(portfolio_id: int):
    """Delete a single portfolio"""
    import sqlite3
    
    conn = sqlite3.connect(simulator.db_path)
    cursor = conn.cursor()
    
    try:
        # Delete trades first (foreign key)
        cursor.execute('DELETE FROM trades_log WHERE portfolio_id = ?', (portfolio_id,))
        
        # Delete positions
        cursor.execute('DELETE FROM positions WHERE portfolio_id = ?', (portfolio_id,))
        
        # Delete snapshots
        cursor.execute('DELETE FROM snapshots WHERE portfolio_id = ?', (portfolio_id,))
        
        # Delete portfolio
        cursor.execute('DELETE FROM portfolios WHERE id = ?', (portfolio_id,))
        
        conn.commit()
    finally:
        conn.close()
    
    return RedirectResponse(url='/simulator', status_code=303)

@app.post("/simulator/delete-all")
async def delete_all_portfolios():
    """Delete all portfolios"""
    import sqlite3
    
    conn = sqlite3.connect(simulator.db_path)
    cursor = conn.cursor()
    
    try:
        # Delete all trades
        cursor.execute('DELETE FROM trades_log')
        
        # Delete all positions
        cursor.execute('DELETE FROM positions')
        
        # Delete all snapshots
        cursor.execute('DELETE FROM snapshots')
        
        # Delete all portfolios
        cursor.execute('DELETE FROM portfolios')
        
        conn.commit()
    finally:
        conn.close()
    
    return RedirectResponse(url='/simulator', status_code=303)

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

@app.get("/live", response_class=HTMLResponse)
async def live_trading():
    """Live trading dashboard"""
    try:
        from live_monitor import LiveMonitor
        import sqlite3
        
        # Load config
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        watchlist = config['watchlist']
        
        # Get live portfolio state
        monitor = LiveMonitor()
        monitor.update_positions_prices(watchlist)
        monitor.calculate_total_value()
        state = monitor.get_portfolio_state()
        
        initial = 10000
        pnl = state['total_value'] - initial
        pnl_pct = (pnl / initial) * 100
        
        # Get recent trades
        conn = sqlite3.connect(monitor.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ticker, action, shares, price, reason, timestamp, pnl
            FROM trades
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        recent_trades = cursor.fetchall()
        conn.close()
        
        # Build trades table HTML
        trades_html = ""
        if recent_trades:
            trades_html = "<table><thead><tr><th>Date</th><th>Action</th><th>Ticker</th><th>Shares</th><th>Prix</th><th>Raison</th><th>P&L</th></tr></thead><tbody>"
            for trade in recent_trades:
                ticker, action, shares, price, reason, timestamp, pnl_trade = trade
                action_color = '#10b981' if action == 'BUY' else '#ef4444'
                pnl_display = f"${pnl_trade:+.2f}" if pnl_trade else "-"
                pnl_class = 'positive' if (pnl_trade and pnl_trade > 0) else 'negative' if pnl_trade else ''
                date_str = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')
                
                trades_html += f"""
                <tr>
                    <td>{date_str}</td>
                    <td style="color: {action_color}; font-weight: bold;">{action}</td>
                    <td>{ticker}</td>
                    <td>{shares}</td>
                    <td>${price:.2f}</td>
                    <td>{reason}</td>
                    <td class="{pnl_class}">{pnl_display}</td>
                </tr>
                """
            trades_html += "</tbody></table>"
        else:
            trades_html = "<p>Aucun trade enregistré</p>"
        
        # Build positions table HTML
        positions_html = ""
        if state['positions']:
            positions_html = "<table><thead><tr><th>Ticker</th><th>Shares</th><th>Prix d'entrée</th><th>Prix actuel</th><th>P&L %</th><th>Valeur</th><th>SL/TP</th></tr></thead><tbody>"
            for pos in state['positions']:
                pnl_class = 'positive' if pos['pnl_pct'] >= 0 else 'negative'
                positions_html += f"""
                <tr>
                    <td style="font-weight: bold;">{pos['ticker']}</td>
                    <td>{pos['shares']}</td>
                    <td>${pos['avg_price']:.2f}</td>
                    <td>${pos['current_price'] or pos['avg_price']:.2f}</td>
                    <td class="{pnl_class}">{pos['pnl_pct']:+.2f}%</td>
                    <td>${pos['value']:,.2f}</td>
                    <td style="font-size: 0.85em;">${pos['stop_loss']:.2f} / ${pos['take_profit']:.2f}</td>
                </tr>
                """
            positions_html += "</tbody></table>"
        else:
            positions_html = "<p>Aucune position ouverte</p>"
        
        # Analyze current signals
        signals_html = ""
        try:
            signals = monitor.analyze_market(watchlist)
            if signals:
                signals_html = "<table><thead><tr><th>Ticker</th><th>Action</th><th>Score</th><th>Prix</th><th>Raison</th></tr></thead><tbody>"
                for sig in signals:
                    action_color = '#10b981' if sig['action'] == 'BUY' else '#ef4444'
                    signals_html += f"""
                    <tr>
                        <td style="font-weight: bold;">{sig['ticker']}</td>
                        <td style="color: {action_color}; font-weight: bold;">{sig['action']}</td>
                        <td>{sig['score']:.1f}/10</td>
                        <td>${sig['price']:.2f}</td>
                        <td>{sig['reason']}</td>
                    </tr>
                    """
                signals_html += "</tbody></table>"
            else:
                signals_html = "<p style='color: #10b981;'>✅ Aucun signal - Toutes les positions dans les objectifs</p>"
        except Exception as e:
            signals_html = f"<p style='color: #ef4444;'>Erreur d'analyse: {str(e)}</p>"
        
    except Exception as e:
        return f"<html><body><h1>Erreur</h1><p>{str(e)}</p></body></html>"
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>Live Trading 🔴</title>
        {COMMON_HEAD}
        <meta http-equiv="refresh" content="300">
        <style>
            .status-indicator {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #10b981;
                animation: pulse 2s infinite;
                margin-right: 8px;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            .warning-box {{
                background: #78350f20;
                border: 2px solid #f59e0b;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1><span class="status-indicator"></span>🔴 Live Trading</h1>
                <p>Paper Trading en Temps Réel</p>
            </header>
            {generate_nav('live')}
            
            <div class="warning-box">
                <strong>⚠️ Mode Paper Trading</strong> - Argent virtuel uniquement. Aucune transaction réelle.
            </div>
            
            <div class="card">
                <div class="card-header">Portfolio Status</div>
                <div class="metric-grid">
                    <div class="metric">
                        <div class="metric-label">💰 Cash</div>
                        <div class="metric-value">${state['cash']:,.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">📊 Valeur Totale</div>
                        <div class="metric-value">${state['total_value']:,.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">📈 P&L</div>
                        <div class="metric-value {'positive' if pnl >= 0 else 'negative'}">${pnl:+,.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Rendement</div>
                        <div class="metric-value {'positive' if pnl_pct >= 0 else 'negative'}">{pnl_pct:+.2f}%</div>
                    </div>
                </div>
                <p style="margin-top: 15px; font-size: 0.9em; color: #94a3b8;">
                    🕐 Dernière mise à jour: {datetime.fromisoformat(state['last_updated']).strftime('%Y-%m-%d %H:%M:%S')}
                    <br>Auto-refresh toutes les 5 minutes
                </p>
            </div>
            
            <div class="card">
                <div class="card-header">📍 Positions Ouvertes ({len(state['positions'])})</div>
                {positions_html}
            </div>
            
            <div class="card">
                <div class="card-header">🚨 Signaux Actuels</div>
                {signals_html}
                <div style="margin-top: 20px;">
                    <form method="post" action="/live/execute" style="display: inline;">
                        <button type="submit" class="btn-primary">⚡ Exécuter les Signaux</button>
                    </form>
                    <button onclick="location.reload()" class="btn-secondary" style="margin-left: 10px;">🔄 Rafraîchir</button>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">📜 Historique des Trades (10 derniers)</div>
                {trades_html}
            </div>
            
            <div class="card">
                <div class="card-header">⚙️ Actions Rapides</div>
                <div class="input-group">
                    <form method="post" action="/live/reset" onsubmit="return confirm('⚠️ Reset le portfolio à $10,000 ?')" style="display: inline;">
                        <button type="submit" class="btn-secondary">🔄 Reset Portfolio</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/live/execute")
async def execute_live_signals():
    """Execute current signals"""
    try:
        from live_monitor import LiveMonitor
        
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        watchlist = config['watchlist']
        
        monitor = LiveMonitor()
        monitor.update_positions_prices(watchlist)
        signals = monitor.analyze_market(watchlist)
        
        results = []
        for signal in signals:
            result = monitor.execute_signal(signal)
            results.append(result)
        
        monitor.calculate_total_value()
        
        return RedirectResponse(url='/live', status_code=303)
    except Exception as e:
        return HTMLResponse(f"<html><body><h1>Erreur</h1><p>{str(e)}</p><a href='/live'>Retour</a></body></html>")

@app.post("/live/reset")
async def reset_live_portfolio():
    """Reset live portfolio"""
    try:
        import os
        from live_monitor import LiveMonitor
        
        monitor = LiveMonitor()
        if os.path.exists(monitor.db_path):
            os.remove(monitor.db_path)
        
        # Recreate empty portfolio
        monitor = LiveMonitor()
        
        return RedirectResponse(url='/live', status_code=303)
    except Exception as e:
        return HTMLResponse(f"<html><body><h1>Erreur</h1><p>{str(e)}</p><a href='/live'>Retour</a></body></html>")

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

@app.get("/settings/telegram", response_class=HTMLResponse)
async def telegram_settings():
    """Telegram configuration page"""
    config = load_config()
    tg = config.get('telegram', {})
    enabled = tg.get('enabled', False)
    bot_token = tg.get('bot_token', '')
    chat_id = tg.get('chat_id', '')
    alert_threshold = tg.get('alert_threshold', 6.0)
    daily_summary_time = tg.get('daily_summary_time', '08:00')

    checked = 'checked' if enabled else ''
    token_masked = f"{bot_token[:10]}...{bot_token[-4:]}" if len(bot_token) > 14 else bot_token

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>Market Analyzer – Telegram Setup</title>
        {COMMON_HEAD}
        <style>
            .tg-form {{ max-width: 600px; margin: 0 auto; }}
            .tg-form .field {{ margin-bottom: 20px; }}
            .tg-form label {{ display: block; margin-bottom: 6px; font-weight: 600; color: #94a3b8; font-size: 0.9em; letter-spacing: 0.05em; text-transform: uppercase; }}
            .tg-form input[type=text], .tg-form input[type=time], .tg-form input[type=number] {{ width: 100%; padding: 12px 16px; border: 2px solid #334155; border-radius: 8px; background: #0f172a; color: #e2e8f0; font-size: 14px; }}
            .tg-form input:focus {{ outline: none; border-color: #667eea; }}
            .toggle-row {{ display: flex; align-items: center; gap: 12px; }}
            .toggle {{ position: relative; width: 50px; height: 26px; }}
            .toggle input {{ opacity: 0; width: 0; height: 0; }}
            .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #334155; border-radius: 26px; transition: 0.3s; }}
            .slider:before {{ position: absolute; content: ""; height: 20px; width: 20px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.3s; }}
            input:checked + .slider {{ background: #10b981; }}
            input:checked + .slider:before {{ transform: translateX(24px); }}
            .actions {{ display: flex; gap: 12px; margin-top: 30px; flex-wrap: wrap; }}
            .alert-box {{ padding: 14px 20px; border-radius: 10px; margin-bottom: 20px; font-size: 0.95em; display: none; }}
            .alert-success {{ background: #065f4620; border: 1px solid #10b981; color: #6ee7b7; display: block; }}
            .alert-error {{ background: #7f1d1d20; border: 1px solid #ef4444; color: #fca5a5; display: block; }}
            .hint {{ font-size: 0.82em; color: #64748b; margin-top: 5px; }}
            .section-divider {{ border: none; border-top: 2px solid #334155; margin: 30px 0; }}
            .test-result {{ margin-top: 15px; padding: 12px 16px; border-radius: 8px; font-size: 0.9em; display: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>✈️ Telegram Setup</h1>
                <p>Configure les notifications de trading sur Telegram</p>
            </header>
            {generate_nav('telegram')}

            <div class="tg-form">
                <div id="save-alert" class="alert-box"></div>

                <div class="card">
                    <div class="card-header">🔑 Connexion Bot</div>

                    <form id="tg-form">
                        <div class="field">
                            <label>Bot Token</label>
                            <input type="text" name="bot_token" id="bot_token"
                                placeholder="123456789:ABCDefghijklmNOPQRSTUvwxyz"
                                value="{bot_token}" autocomplete="off" />
                            <div class="hint">Obtenu via <strong>@BotFather</strong> sur Telegram. Ex: <code>123456:ABC...</code></div>
                        </div>

                        <div class="field">
                            <label>Chat ID</label>
                            <input type="text" name="chat_id" id="chat_id"
                                placeholder="-100123456789 ou 6812190723"
                                value="{chat_id}" />
                            <div class="hint">Ton ID perso ou l'ID d'un groupe/canal. Utilise <strong>@userinfobot</strong> pour le trouver.</div>
                        </div>

                        <hr class="section-divider">

                        <div class="card-header">⚙️ Paramètres</div>

                        <div class="field">
                            <div class="toggle-row">
                                <label class="toggle">
                                    <input type="checkbox" name="enabled" id="enabled" {checked}>
                                    <span class="slider"></span>
                                </label>
                                <span>Notifications activées</span>
                            </div>
                        </div>

                        <div class="field">
                            <label>Seuil d'alerte (score minimum)</label>
                            <input type="number" name="alert_threshold" id="alert_threshold"
                                min="0" max="10" step="0.5" value="{alert_threshold}" />
                            <div class="hint">Envoie une alerte quand un signal dépasse ce score (sur 10).</div>
                        </div>

                        <div class="field">
                            <label>Résumé quotidien à</label>
                            <input type="time" name="daily_summary_time" id="daily_summary_time"
                                value="{daily_summary_time}" />
                            <div class="hint">Heure d'envoi du résumé journalier du portfolio.</div>
                        </div>

                        <div class="actions">
                            <button type="button" class="btn-primary" onclick="saveSettings()">💾 Sauvegarder</button>
                            <button type="button" class="btn-success" onclick="sendTest()">🧪 Test notification</button>
                        </div>
                    </form>

                    <div id="test-result" class="test-result"></div>
                </div>
            </div>
        </div>

        <script>
        async function saveSettings() {{
            const form = document.getElementById('tg-form');
            const data = new FormData(form);

            // Checkbox fix: not included in FormData when unchecked
            if (!form.querySelector('#enabled').checked) {{
                data.set('enabled', 'false');
            }} else {{
                data.set('enabled', 'true');
            }}

            const resp = await fetch('/settings/telegram/save', {{
                method: 'POST',
                body: data
            }});
            const result = await resp.json();
            const box = document.getElementById('save-alert');
            box.className = 'alert-box ' + (result.success ? 'alert-success' : 'alert-error');
            box.textContent = result.message;
            box.style.display = 'block';
            setTimeout(() => box.style.display = 'none', 4000);
        }}

        async function sendTest() {{
            const botToken = document.getElementById('bot_token').value.trim();
            const chatId = document.getElementById('chat_id').value.trim();

            const data = new FormData();
            data.append('bot_token', botToken);
            data.append('chat_id', chatId);

            const resultBox = document.getElementById('test-result');
            resultBox.style.display = 'block';
            resultBox.style.background = '#1e293b';
            resultBox.style.border = '1px solid #334155';
            resultBox.style.color = '#94a3b8';
            resultBox.textContent = '⏳ Envoi en cours...';

            const resp = await fetch('/settings/telegram/test', {{
                method: 'POST',
                body: data
            }});
            const result = await resp.json();

            if (result.success) {{
                resultBox.style.background = '#065f4620';
                resultBox.style.border = '1px solid #10b981';
                resultBox.style.color = '#6ee7b7';
                resultBox.textContent = '✅ ' + result.message;
            }} else {{
                resultBox.style.background = '#7f1d1d20';
                resultBox.style.border = '1px solid #ef4444';
                resultBox.style.color = '#fca5a5';
                resultBox.textContent = '❌ ' + result.message;
            }}
        }}
        </script>
    </body>
    </html>
    """

@app.post("/settings/telegram/save")
async def save_telegram_settings(
    bot_token: str = Form(''),
    chat_id: str = Form(''),
    enabled: str = Form('false'),
    alert_threshold: float = Form(6.0),
    daily_summary_time: str = Form('08:00')
):
    """Save Telegram configuration to config.json"""
    try:
        config = load_config()
        config['telegram'] = {
            'enabled': enabled == 'true',
            'bot_token': bot_token.strip(),
            'chat_id': chat_id.strip(),
            'alert_threshold': alert_threshold,
            'daily_summary_time': daily_summary_time
        }
        save_config(config)
        return JSONResponse({'success': True, 'message': '✅ Configuration sauvegardée !'})
    except Exception as e:
        return JSONResponse({'success': False, 'message': f'Erreur: {str(e)}'})

@app.post("/settings/telegram/test")
async def test_telegram_notification(
    bot_token: str = Form(''),
    chat_id: str = Form('')
):
    """Send a test message to Telegram"""
    import urllib.request
    import urllib.parse

    bot_token = bot_token.strip()
    chat_id = chat_id.strip()

    if not bot_token or not chat_id:
        return JSONResponse({'success': False, 'message': 'Bot token et Chat ID requis.'})

    try:
        text = (
            "🧪 *Test Market Analyzer*\n\n"
            "✅ Connexion Telegram configurée avec succès !\n"
            f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            "_Market Analyzer est prêt à t'envoyer des alertes._"
        )
        payload = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }).encode()

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        req = urllib.request.Request(url, data=payload, method='POST')
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())

        if result.get('ok'):
            return JSONResponse({'success': True, 'message': 'Message envoyé ! Vérifie ton Telegram.'})
        else:
            return JSONResponse({'success': False, 'message': result.get('description', 'Erreur inconnue')})
    except Exception as e:
        return JSONResponse({'success': False, 'message': str(e)})


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--host', default='0.0.0.0')
    args = parser.parse_args()
    
    print(f"\n🚀 Starting Advanced Market Analyzer Dashboard...")
    print(f"📍 http://0.0.0.0:{args.port}")
    print(f"\n💡 Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == '__main__':
    main()
