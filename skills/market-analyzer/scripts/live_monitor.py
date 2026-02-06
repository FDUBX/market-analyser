#!/usr/bin/env python3
"""
Live Market Monitor - Paper Trading with Telegram Alerts
Analyzes stocks in real-time and manages a virtual portfolio
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from analyzer import MarketAnalyzer
from data_cache import DataCache
import sqlite3
import json
from datetime import datetime, timedelta
import argparse

class LiveMonitor:
    def __init__(self, db_path="live_portfolio.db"):
        self.db_path = db_path
        self.analyzer = MarketAnalyzer(use_cache=True)
        self.cache = DataCache()
        self._init_db()
        
    def _init_db(self):
        """Initialize live portfolio database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Portfolio state
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY,
                cash REAL NOT NULL,
                total_value REAL NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # Current positions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                ticker TEXT PRIMARY KEY,
                shares INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                current_price REAL,
                entry_date TEXT NOT NULL,
                entry_score REAL,
                stop_loss REAL,
                take_profit REAL
            )
        ''')
        
        # Trade history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                shares INTEGER NOT NULL,
                price REAL NOT NULL,
                score REAL,
                reason TEXT,
                timestamp TEXT NOT NULL,
                pnl REAL
            )
        ''')
        
        # Signals log (for review)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                score REAL NOT NULL,
                price REAL NOT NULL,
                timestamp TEXT NOT NULL,
                executed BOOLEAN DEFAULT 0
            )
        ''')
        
        # Initialize portfolio if empty
        cursor.execute('SELECT COUNT(*) FROM portfolio')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO portfolio (id, cash, total_value, last_updated)
                VALUES (1, 10000.0, 10000.0, ?)
            ''', (datetime.now().isoformat(),))
        
        conn.commit()
        conn.close()
        
    def get_portfolio_state(self):
        """Get current portfolio state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT cash, total_value, last_updated FROM portfolio WHERE id = 1')
        cash, total_value, last_updated = cursor.fetchone()
        
        cursor.execute('SELECT ticker, shares, avg_price, current_price, entry_date, stop_loss, take_profit FROM positions')
        positions = []
        for row in cursor.fetchall():
            positions.append({
                'ticker': row[0],
                'shares': row[1],
                'avg_price': row[2],
                'current_price': row[3],
                'entry_date': row[4],
                'stop_loss': row[5],
                'take_profit': row[6],
                'value': (row[3] or row[2]) * row[1],
                'pnl_pct': ((row[3] or row[2]) - row[2]) / row[2] * 100 if row[2] > 0 else 0
            })
        
        conn.close()
        
        return {
            'cash': cash,
            'total_value': total_value,
            'positions': positions,
            'last_updated': last_updated
        }
    
    def update_positions_prices(self, watchlist):
        """Update current prices for all positions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for ticker in watchlist:
            # Get latest price from cache
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            data = self.cache.get_cached_data(ticker, start_date, end_date)
            
            if not data.empty:
                current_price = float(data['Close'].iloc[-1])
                cursor.execute('''
                    UPDATE positions 
                    SET current_price = ?
                    WHERE ticker = ?
                ''', (current_price, ticker))
        
        conn.commit()
        conn.close()
    
    def analyze_market(self, watchlist, config_path="../config.json"):
        """Analyze all stocks and generate signals"""
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        buy_threshold = config['thresholds']['buy']
        sell_threshold = config['thresholds']['sell']
        
        signals = []
        
        for ticker in watchlist:
            analysis = self.analyzer.analyze_stock(ticker)
            
            if 'error' in analysis:
                continue
            
            score = float(analysis['scores']['total'])
            price = float(analysis['current_price'])
            
            # Check if we have a position
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT shares, avg_price, stop_loss, take_profit FROM positions WHERE ticker = ?', (ticker,))
            position = cursor.fetchone()
            conn.close()
            
            if position:
                # We have a position - check exit signals
                shares, avg_price, stop_loss, take_profit = position
                pnl_pct = (price - avg_price) / avg_price * 100
                
                # Check stop-loss
                if price <= stop_loss:
                    signals.append({
                        'ticker': ticker,
                        'action': 'SELL',
                        'reason': 'STOP_LOSS',
                        'score': score,
                        'price': price,
                        'shares': shares,
                        'pnl_pct': pnl_pct
                    })
                # Check take-profit
                elif price >= take_profit:
                    signals.append({
                        'ticker': ticker,
                        'action': 'SELL',
                        'reason': 'TAKE_PROFIT',
                        'score': score,
                        'price': price,
                        'shares': shares,
                        'pnl_pct': pnl_pct
                    })
                # Check score-based exit
                elif score <= sell_threshold:
                    signals.append({
                        'ticker': ticker,
                        'action': 'SELL',
                        'reason': 'LOW_SCORE',
                        'score': score,
                        'price': price,
                        'shares': shares,
                        'pnl_pct': pnl_pct
                    })
            else:
                # No position - check buy signal
                if score >= buy_threshold:
                    signals.append({
                        'ticker': ticker,
                        'action': 'BUY',
                        'reason': 'HIGH_SCORE',
                        'score': score,
                        'price': price
                    })
        
        return signals
    
    def execute_signal(self, signal, config_path="../config.json"):
        """Execute a trading signal (paper trading)"""
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        position_size = config['backtest']['position_size']
        stop_loss_pct = config['backtest']['stop_loss']
        take_profit_pct = config['backtest']['take_profit']
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current portfolio state
        cursor.execute('SELECT cash, total_value FROM portfolio WHERE id = 1')
        cash, total_value = cursor.fetchone()
        
        if signal['action'] == 'BUY':
            # Calculate position size
            position_value = total_value * position_size
            shares = int(position_value / signal['price'])
            cost = shares * signal['price']
            
            if cost <= cash and shares > 0:
                # Execute buy
                cash -= cost
                
                # Calculate stop-loss and take-profit
                stop_loss = signal['price'] * (1 - stop_loss_pct)
                take_profit = signal['price'] * (1 + take_profit_pct)
                
                # Add position
                cursor.execute('''
                    INSERT OR REPLACE INTO positions 
                    (ticker, shares, avg_price, current_price, entry_date, entry_score, stop_loss, take_profit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (signal['ticker'], shares, signal['price'], signal['price'], 
                      datetime.now().isoformat(), signal['score'], stop_loss, take_profit))
                
                # Log trade
                cursor.execute('''
                    INSERT INTO trades (ticker, action, shares, price, score, reason, timestamp, pnl)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (signal['ticker'], 'BUY', shares, signal['price'], signal['score'], 
                      signal['reason'], datetime.now().isoformat(), 0))
                
                # Update portfolio
                cursor.execute('UPDATE portfolio SET cash = ?, last_updated = ? WHERE id = 1',
                             (cash, datetime.now().isoformat()))
                
                conn.commit()
                result = f"✅ BUY {shares} {signal['ticker']} @ ${signal['price']:.2f}"
            else:
                result = f"❌ Insufficient cash for {signal['ticker']}"
        
        elif signal['action'] == 'SELL':
            # Get position
            cursor.execute('SELECT shares, avg_price FROM positions WHERE ticker = ?', (signal['ticker'],))
            position = cursor.fetchone()
            
            if position:
                shares, avg_price = position
                proceeds = shares * signal['price']
                pnl = proceeds - (shares * avg_price)
                pnl_pct = (signal['price'] - avg_price) / avg_price * 100
                
                # Execute sell
                cash += proceeds
                
                # Remove position
                cursor.execute('DELETE FROM positions WHERE ticker = ?', (signal['ticker'],))
                
                # Log trade
                cursor.execute('''
                    INSERT INTO trades (ticker, action, shares, price, score, reason, timestamp, pnl)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (signal['ticker'], 'SELL', shares, signal['price'], signal['score'],
                      signal['reason'], datetime.now().isoformat(), pnl))
                
                # Update portfolio
                cursor.execute('UPDATE portfolio SET cash = ?, last_updated = ? WHERE id = 1',
                             (cash, datetime.now().isoformat()))
                
                conn.commit()
                result = f"✅ SELL {shares} {signal['ticker']} @ ${signal['price']:.2f} ({pnl_pct:+.2f}%)"
            else:
                result = f"❌ No position in {signal['ticker']}"
        
        conn.close()
        return result
    
    def calculate_total_value(self):
        """Calculate total portfolio value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT cash FROM portfolio WHERE id = 1')
        cash = cursor.fetchone()[0]
        
        cursor.execute('SELECT ticker, shares, current_price, avg_price FROM positions')
        positions_value = 0
        for ticker, shares, current_price, avg_price in cursor.fetchall():
            price = current_price if current_price else avg_price
            positions_value += shares * price
        
        total_value = cash + positions_value
        
        cursor.execute('UPDATE portfolio SET total_value = ?, last_updated = ? WHERE id = 1',
                     (total_value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return total_value

def main():
    parser = argparse.ArgumentParser(description='Live Market Monitor')
    parser.add_argument('--analyze', action='store_true', help='Analyze market and show signals')
    parser.add_argument('--execute', action='store_true', help='Execute signals automatically')
    parser.add_argument('--status', action='store_true', help='Show portfolio status')
    parser.add_argument('--reset', action='store_true', help='Reset portfolio to $10,000')
    args = parser.parse_args()
    
    monitor = LiveMonitor()
    
    # Load watchlist
    with open('../config.json', 'r') as f:
        config = json.load(f)
    watchlist = config['watchlist']
    
    if args.reset:
        print("🔄 Resetting portfolio...")
        os.remove(monitor.db_path)
        monitor = LiveMonitor()
        print("✅ Portfolio reset to $10,000")
        return
    
    if args.status:
        state = monitor.get_portfolio_state()
        monitor.update_positions_prices(watchlist)
        monitor.calculate_total_value()
        state = monitor.get_portfolio_state()
        
        print(f"\n💼 Portfolio Status")
        print(f"{'='*60}")
        print(f"💰 Cash: ${state['cash']:,.2f}")
        print(f"📊 Total Value: ${state['total_value']:,.2f}")
        initial = 10000
        pnl = state['total_value'] - initial
        pnl_pct = (pnl / initial) * 100
        print(f"📈 P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
        print(f"🕐 Last Updated: {state['last_updated']}")
        
        if state['positions']:
            print(f"\n📍 Positions:")
            print(f"{'Ticker':<8} {'Shares':<8} {'Entry':<10} {'Current':<10} {'P&L %':<10} {'Value':<12}")
            print("-" * 60)
            for pos in state['positions']:
                print(f"{pos['ticker']:<8} {pos['shares']:<8} ${pos['avg_price']:<9.2f} "
                      f"${pos['current_price'] or pos['avg_price']:<9.2f} "
                      f"{pos['pnl_pct']:>+8.2f}% ${pos['value']:>10.2f}")
        else:
            print("\n📍 No open positions")
        
        return
    
    if args.analyze:
        print(f"\n🔍 Analyzing {len(watchlist)} stocks...")
        monitor.update_positions_prices(watchlist)
        signals = monitor.analyze_market(watchlist)
        
        if signals:
            print(f"\n🚨 {len(signals)} Signal(s) Found:\n")
            for signal in signals:
                if signal['action'] == 'BUY':
                    print(f"🟢 BUY {signal['ticker']}")
                    print(f"   Score: {signal['score']:.1f}/10")
                    print(f"   Price: ${signal['price']:.2f}")
                    print(f"   Reason: {signal['reason']}")
                else:
                    print(f"🔴 SELL {signal['ticker']}")
                    print(f"   Score: {signal['score']:.1f}/10")
                    print(f"   Price: ${signal['price']:.2f}")
                    print(f"   P&L: {signal['pnl_pct']:+.2f}%")
                    print(f"   Reason: {signal['reason']}")
                print()
            
            if args.execute:
                print("⚡ Executing signals...\n")
                for signal in signals:
                    result = monitor.execute_signal(signal)
                    print(result)
                
                monitor.calculate_total_value()
                print("\n✅ All signals executed")
        else:
            print("✅ No signals - all positions within targets")

if __name__ == '__main__':
    main()
