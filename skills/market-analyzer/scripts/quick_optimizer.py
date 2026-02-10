#!/usr/bin/env python3
"""
Quick optimizer - Test multiple configurations fast
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_sim import PortfolioSimulator
import sqlite3
import json
from itertools import product

def test_config(name, config, start_date, end_date):
    """Test a single configuration"""
    sim = PortfolioSimulator()
    
    # Create portfolio
    conn = sqlite3.connect(sim.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO portfolios (name, initial_capital, current_capital, start_date, mode, config)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, 10000, 10000, start_date, 'backtest', json.dumps(config)))
    
    conn.commit()
    portfolio_id = cursor.lastrowid
    conn.close()
    
    # Run simulation
    print(f"\n🧪 Testing: {name}")
    print(f"   BUY={config['buy_threshold']:.1f} SELL={config['sell_threshold']:.1f} | "
          f"SL={config['stop_loss']:.0%} TP={config['take_profit']:.0%}")
    
    sim.run_simulation(portfolio_id, end_date=end_date)
    
    # Get results
    conn = sqlite3.connect(sim.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT current_capital, 
               (SELECT COUNT(*) FROM trades_log WHERE portfolio_id = ?)
        FROM portfolios WHERE id = ?
    ''', (portfolio_id, portfolio_id))
    
    final_value, num_trades = cursor.fetchone()
    return_pct = ((final_value - 10000) / 10000) * 100
    
    # Calculate win rate
    cursor.execute('''
        SELECT COUNT(*) FROM trades_log 
        WHERE portfolio_id = ? AND pnl_pct > 0
    ''', (portfolio_id,))
    wins = cursor.fetchone()[0]
    win_rate = (wins / num_trades * 100) if num_trades > 0 else 0
    
    conn.close()
    
    print(f"   ✅ Return: {return_pct:+.2f}% | Trades: {num_trades} | Win rate: {win_rate:.1f}%")
    
    return {
        'name': name,
        'config': config,
        'return_pct': return_pct,
        'num_trades': num_trades,
        'win_rate': win_rate,
        'final_value': final_value
    }

def main():
    print("\n🔬 BALANCED STRATEGY OPTIMIZER")
    print("=" * 60)
    
    # Base config
    base_weights = {"technical": 0.4, "fundamental": 0.4, "sentiment": 0.2}
    
    # Test configurations
    configs = []
    
    # Vary thresholds
    buy_thresholds = [5.3, 5.5, 5.7]
    sell_thresholds = [4.3, 4.5, 4.7]
    
    # Vary risk params
    stop_losses = [0.04, 0.05, 0.06]
    take_profits = [0.12, 0.15, 0.18]
    
    test_num = 1
    for buy, sell, sl, tp in product(buy_thresholds, sell_thresholds, stop_losses, take_profits):
        if sell >= buy:  # Skip invalid
            continue
        
        config = {
            'buy_threshold': buy,
            'sell_threshold': sell,
            'weights': base_weights,
            'position_size': 0.20,
            'stop_loss': sl,
            'take_profit': tp
        }
        
        configs.append(config)
    
    print(f"\n📊 Testing {len(configs)} configurations...\n")
    
    results = []
    for i, config in enumerate(configs, 1):
        name = f"Opt_{i:02d}"
        try:
            result = test_config(name, config, "2024-01-01", "2024-12-31")
            results.append(result)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # Sort by return
    results.sort(key=lambda x: x['return_pct'], reverse=True)
    
    print("\n" + "=" * 60)
    print("🏆 TOP 5 CONFIGURATIONS")
    print("=" * 60)
    
    for i, r in enumerate(results[:5], 1):
        cfg = r['config']
        print(f"\n{i}. {r['name']} → Return: {r['return_pct']:+.2f}%")
        print(f"   BUY: {cfg['buy_threshold']:.1f} | SELL: {cfg['sell_threshold']:.1f}")
        print(f"   Stop-loss: {cfg['stop_loss']:.0%} | Take-profit: {cfg['take_profit']:.0%}")
        print(f"   Trades: {r['num_trades']} | Win rate: {r['win_rate']:.1f}%")
        print(f"   Final value: ${r['final_value']:,.2f}")
    
    if results:
        print("\n" + "=" * 60)
        print("💡 BEST CONFIG:")
        best = results[0]
        print(json.dumps(best['config'], indent=2))

if __name__ == '__main__':
    main()
