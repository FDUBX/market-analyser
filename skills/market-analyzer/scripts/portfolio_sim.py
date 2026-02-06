#!/usr/bin/env python3
"""
Portfolio Simulator - Simulate trading strategy with virtual capital
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import json
import argparse
from analyzer import MarketAnalyzer

# Import cache
try:
    from data_cache import DataCache
    USE_CACHE = True
except ImportError:
    USE_CACHE = False
    print("⚠️  Warning: data_cache not available, will use direct API calls")

class PortfolioSimulator:
    def __init__(self, db_path='portfolio_sim.db'):
        self.db_path = db_path
        self.analyzer = MarketAnalyzer()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Portfolios table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                initial_capital REAL NOT NULL,
                current_capital REAL NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                mode TEXT NOT NULL,
                config TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                entry_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                shares INTEGER NOT NULL,
                capital_invested REAL NOT NULL,
                exit_date TEXT,
                exit_price REAL,
                exit_reason TEXT,
                pnl REAL,
                pnl_pct REAL,
                status TEXT DEFAULT 'open',
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        ''')
        
        # Daily snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                total_value REAL NOT NULL,
                cash REAL NOT NULL,
                positions_value REAL NOT NULL,
                num_positions INTEGER NOT NULL,
                daily_return_pct REAL,
                total_return_pct REAL,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        ''')
        
        # Trades log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                action TEXT NOT NULL,
                ticker TEXT NOT NULL,
                price REAL NOT NULL,
                shares INTEGER NOT NULL,
                value REAL NOT NULL,
                score REAL,
                signal TEXT,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_portfolio(self, name, initial_capital, start_date, mode='historical', config=None):
        """Create a new portfolio simulation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO portfolios (name, initial_capital, current_capital, start_date, mode, config)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, initial_capital, initial_capital, start_date, mode, json.dumps(config or {})))
            
            portfolio_id = cursor.lastrowid
            conn.commit()
            
            return {
                'success': True,
                'portfolio_id': portfolio_id,
                'name': name,
                'initial_capital': initial_capital,
                'start_date': start_date
            }
        except sqlite3.IntegrityError:
            return {'success': False, 'error': f'Portfolio "{name}" already exists'}
        finally:
            conn.close()
    
    def run_simulation(self, portfolio_id, end_date=None, universe=None):
        """Run portfolio simulation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get portfolio
        cursor.execute('SELECT * FROM portfolios WHERE id = ?', (portfolio_id,))
        portfolio = cursor.fetchone()
        
        if not portfolio:
            conn.close()
            return {'error': 'Portfolio not found'}
        
        portfolio_id, name, initial_capital, current_capital, start_date, _, mode, config_str, _ = portfolio
        config = json.loads(config_str) if config_str else {}
        
        # Default config
        position_size = config.get('position_size', 0.2)
        stop_loss = config.get('stop_loss', 0.05)
        take_profit = config.get('take_profit', 0.15)
        # Load global config if not specified in portfolio config
        global_config = {}
        try:
            import os
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
            with open(config_path, 'r') as f:
                global_config = json.load(f)
        except:
            pass
        
        buy_threshold = config.get('buy_threshold', global_config.get('thresholds', {}).get('buy', 5.5))
        sell_threshold = config.get('sell_threshold', global_config.get('thresholds', {}).get('sell', 4.5))
        
        # Default universe
        if universe is None:
            universe = config.get('universe', ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMZN', 'META'])
        
        # Determine date range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.now()
        
        # Preload data if cache is available
        if USE_CACHE:
            cache = DataCache()
            print(f"📥 Préchargement des données pour {len(universe)} actions...")
            success, failed = cache.preload_universe(universe, start, end)
            if failed:
                print(f"⚠️  Échec pour: {', '.join(failed)}")
        
        # Load existing positions
        cursor.execute('SELECT * FROM positions WHERE portfolio_id = ? AND status = "open"', (portfolio_id,))
        open_positions = {row[2]: row for row in cursor.fetchall()}  # ticker -> position data
        
        cash = current_capital
        
        # Iterate through dates
        current_date = start
        trades_made = []
        
        def get_price_for_date(ticker, d):
            """Get closing price for ticker on date d. If no data (holiday/weekend), use last known close (forward-fill)."""
            if USE_CACHE:
                cache = DataCache()
                hist = cache.get_cached_data(ticker, d, d + timedelta(days=1))
                if not hist.empty:
                    return hist['Close'].iloc[0]
                _, close = cache.get_last_close_before_or_on(ticker, d)
                return close
            else:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=d - timedelta(days=10), end=d + timedelta(days=1))
                if hist.empty:
                    return None
                # Last available close on or before d (handles holidays/weekends)
                cut = pd.Timestamp(d).normalize()
                on_or_before = hist[hist.index.normalize() <= cut]
                if on_or_before.empty:
                    return None
                return float(on_or_before['Close'].iloc[-1])
        
        print(f"\n🔄 Running simulation for portfolio '{name}'...")
        print(f"📅 Period: {start_date} → {end_date or 'today'}")
        print(f"💰 Initial capital: ${initial_capital:,.2f}")
        print(f"🎯 Universe: {', '.join(universe)}\n")
        
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Check existing positions for exits
            for ticker, position_data in list(open_positions.items()):
                pos_id, _, _, entry_date, entry_price, shares, capital_invested, _, _, _, _, _, status = position_data
                
                try:
                    current_price = get_price_for_date(ticker, current_date)
                    if current_price is None:
                        continue
                    pnl_pct = (current_price - entry_price) / entry_price
                    
                    # Check exit conditions
                    should_exit = False
                    exit_reason = None
                    
                    # Stop loss / take profit
                    if pnl_pct <= -stop_loss:
                        should_exit = True
                        exit_reason = 'STOP_LOSS'
                    elif pnl_pct >= take_profit:
                        should_exit = True
                        exit_reason = 'TAKE_PROFIT'
                    else:
                        # Check score for sell signal
                        analysis = self.analyzer.analyze_stock(ticker)
                        if 'error' not in analysis and analysis['scores']['total'] <= sell_threshold:
                            should_exit = True
                            exit_reason = 'SELL_SIGNAL'
                    
                    if should_exit:
                        # Exit position
                        exit_value = shares * current_price
                        cash += exit_value
                        pnl = exit_value - capital_invested
                        pnl_pct_val = (pnl / capital_invested) * 100
                        
                        # Update position
                        cursor.execute('''
                            UPDATE positions
                            SET exit_date = ?, exit_price = ?, exit_reason = ?, pnl = ?, pnl_pct = ?, status = 'closed'
                            WHERE id = ?
                        ''', (date_str, current_price, exit_reason, pnl, pnl_pct_val, pos_id))
                        
                        # Log trade
                        cursor.execute('''
                            INSERT INTO trades_log (portfolio_id, date, action, ticker, price, shares, value, signal)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (portfolio_id, date_str, 'SELL', ticker, current_price, shares, exit_value, exit_reason))
                        
                        del open_positions[ticker]
                        trades_made.append({
                            'date': date_str,
                            'action': 'SELL',
                            'ticker': ticker,
                            'price': current_price,
                            'shares': shares,
                            'pnl_pct': pnl_pct_val,
                            'reason': exit_reason
                        })
                        
                        print(f"📉 {date_str} SELL {ticker} @ ${current_price:.2f} ({exit_reason}) → PnL: {pnl_pct_val:+.2f}%")
                
                except Exception as e:
                    print(f"⚠️  Error checking {ticker}: {e}")
                    continue
            
            # Scan universe for new opportunities
            for ticker in universe:
                # Skip if already have position
                if ticker in open_positions:
                    continue
                
                try:
                    analysis = self.analyzer.analyze_stock(ticker)
                    
                    if 'error' in analysis:
                        continue
                    
                    score = analysis['scores']['total']
                    
                    # Check buy signal
                    if score >= buy_threshold:
                        # Calculate position size
                        capital_to_invest = cash * position_size
                        
                        if capital_to_invest < 100:  # Minimum investment
                            continue
                        
                        # Get current price (forward-fill if market closed)
                        current_price = get_price_for_date(ticker, current_date)
                        if current_price is None:
                            continue
                        shares = int(capital_to_invest / current_price)
                        
                        if shares == 0:
                            continue
                        
                        actual_investment = shares * current_price
                        cash -= actual_investment
                        
                        # Create position
                        cursor.execute('''
                            INSERT INTO positions (portfolio_id, ticker, entry_date, entry_price, shares, capital_invested, status)
                            VALUES (?, ?, ?, ?, ?, ?, 'open')
                        ''', (portfolio_id, ticker, date_str, current_price, shares, actual_investment))
                        
                        position_id = cursor.lastrowid
                        
                        # Log trade
                        cursor.execute('''
                            INSERT INTO trades_log (portfolio_id, date, action, ticker, price, shares, value, score, signal)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (portfolio_id, date_str, 'BUY', ticker, current_price, shares, actual_investment, score, 'BUY'))
                        
                        # Update open positions
                        cursor.execute('SELECT * FROM positions WHERE id = ?', (position_id,))
                        open_positions[ticker] = cursor.fetchone()
                        
                        trades_made.append({
                            'date': date_str,
                            'action': 'BUY',
                            'ticker': ticker,
                            'price': current_price,
                            'shares': shares,
                            'score': score
                        })
                        
                        print(f"📈 {date_str} BUY {ticker} @ ${current_price:.2f} (Score: {score:.1f}) → {shares} shares")
                
                except Exception as e:
                    print(f"⚠️  Error analyzing {ticker}: {e}")
                    continue
            
            # Calculate daily snapshot (use last known close if no data for this date → avoids fake drops on holidays)
            positions_value = 0
            for ticker, position_data in open_positions.items():
                try:
                    current_price = get_price_for_date(ticker, current_date)
                    if current_price is not None:
                        shares = position_data[5]
                        positions_value += shares * current_price
                except Exception:
                    pass
            
            total_value = cash + positions_value
            total_return_pct = ((total_value - initial_capital) / initial_capital) * 100
            
            # Save snapshot
            cursor.execute('''
                INSERT INTO snapshots (portfolio_id, date, total_value, cash, positions_value, num_positions, total_return_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (portfolio_id, date_str, total_value, cash, positions_value, len(open_positions), total_return_pct))
            
            # Move to next day (skip weekends)
            current_date += timedelta(days=1)
            while current_date.weekday() >= 5:  # Saturday=5, Sunday=6
                current_date += timedelta(days=1)
        
        # Update portfolio
        cursor.execute('''
            UPDATE portfolios
            SET current_capital = ?, end_date = ?
            WHERE id = ?
        ''', (cash + positions_value, end_date or datetime.now().strftime('%Y-%m-%d'), portfolio_id))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'portfolio_id': portfolio_id,
            'trades_made': len(trades_made),
            'final_value': cash + positions_value,
            'return_pct': total_return_pct
        }
    
    def get_portfolio_status(self, portfolio_id):
        """Get current portfolio status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get portfolio info
        cursor.execute('SELECT * FROM portfolios WHERE id = ?', (portfolio_id,))
        portfolio = cursor.fetchone()
        
        if not portfolio:
            conn.close()
            return {'error': 'Portfolio not found'}
        
        portfolio_id, name, initial_capital, current_capital, start_date, end_date, mode, config_str, created_at = portfolio
        
        # Get open positions
        cursor.execute('SELECT * FROM positions WHERE portfolio_id = ? AND status = "open"', (portfolio_id,))
        open_positions = cursor.fetchall()
        
        # Get closed positions
        cursor.execute('SELECT * FROM positions WHERE portfolio_id = ? AND status = "closed"', (portfolio_id,))
        closed_positions = cursor.fetchall()
        
        # Get latest snapshot
        cursor.execute('''
            SELECT * FROM snapshots WHERE portfolio_id = ? ORDER BY date DESC LIMIT 1
        ''', (portfolio_id,))
        latest_snapshot = cursor.fetchone()
        
        conn.close()
        
        return {
            'portfolio_id': portfolio_id,
            'name': name,
            'initial_capital': initial_capital,
            'current_capital': current_capital,
            'start_date': start_date,
            'end_date': end_date,
            'mode': mode,
            'open_positions': len(open_positions),
            'closed_positions': len(closed_positions),
            'latest_snapshot': latest_snapshot
        }
    
    def list_portfolios(self):
        """List all portfolios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, initial_capital, current_capital, start_date, end_date, mode FROM portfolios')
        portfolios = cursor.fetchall()
        
        conn.close()
        
        return portfolios


def main():
    parser = argparse.ArgumentParser(description='Portfolio Simulator')
    parser.add_argument('command', choices=['create', 'run', 'status', 'list'], help='Command')
    parser.add_argument('--name', help='Portfolio name')
    parser.add_argument('--capital', type=float, default=10000, help='Initial capital')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--id', type=int, help='Portfolio ID')
    parser.add_argument('--universe', nargs='+', help='Stock universe')
    
    args = parser.parse_args()
    
    sim = PortfolioSimulator()
    
    if args.command == 'create':
        if not args.name or not args.start:
            print("❌ --name and --start are required")
            return
        
        result = sim.create_portfolio(args.name, args.capital, args.start)
        if result['success']:
            print(f"✅ Portfolio created: {result['name']} (ID: {result['portfolio_id']})")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif args.command == 'run':
        if not args.id:
            print("❌ --id is required")
            return
        
        result = sim.run_simulation(args.id, args.end, args.universe)
        if result.get('success'):
            print(f"\n✅ Simulation complete!")
            print(f"Trades executed: {result['trades_made']}")
            print(f"Final value: ${result['final_value']:,.2f}")
            print(f"Return: {result['return_pct']:+.2f}%")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    elif args.command == 'status':
        if not args.id:
            print("❌ --id is required")
            return
        
        status = sim.get_portfolio_status(args.id)
        if 'error' in status:
            print(f"❌ {status['error']}")
        else:
            print(f"\n📊 Portfolio: {status['name']}")
            print(f"Initial: ${status['initial_capital']:,.2f}")
            print(f"Current: ${status['current_capital']:,.2f}")
            print(f"Period: {status['start_date']} → {status['end_date'] or 'ongoing'}")
            print(f"Open positions: {status['open_positions']}")
            print(f"Closed positions: {status['closed_positions']}")
    
    elif args.command == 'list':
        portfolios = sim.list_portfolios()
        if portfolios:
            print("\n📋 Portfolios:\n")
            for p in portfolios:
                print(f"ID {p[0]}: {p[1]} | ${p[2]:,.0f} → ${p[3]:,.0f} | {p[4]} → {p[5] or 'ongoing'} ({p[6]})")
        else:
            print("No portfolios found")


if __name__ == '__main__':
    main()
