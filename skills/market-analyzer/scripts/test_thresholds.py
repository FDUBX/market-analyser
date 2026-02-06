#!/usr/bin/env python3
"""Test multiple BUY/SELL thresholds"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from portfolio_sim import PortfolioSimulator
import sqlite3
import json

sim = PortfolioSimulator()

# Test different thresholds
thresholds_to_test = [
    (5.4, 4.4, "v2.1 T5.4"),
    (5.5, 4.5, "v2.1 T5.5"),
    (5.6, 4.6, "v2.1 T5.6"),
]

print("\n🔬 Testing Multiple Thresholds on 2024\n")

results = []

for buy_thresh, sell_thresh, name in thresholds_to_test:
    # Create portfolio with custom config
    config = {
        "buy_threshold": buy_thresh,
        "sell_threshold": sell_thresh,
        "position_size": 0.20,
        "stop_loss": 0.05,
        "take_profit": 0.18,
        "weights": {"technical": 0.4, "fundamental": 0.4, "sentiment": 0.2}
    }
    
    print(f"Testing BUY={buy_thresh}, SELL={sell_thresh}...")
    result = sim.create_portfolio(name, 10000, "2024-01-01", config=config)
    pid = result['portfolio_id']
    
    sim.run_simulation(pid, end_date="2024-12-31")
    
    # Get results
    conn = sqlite3.connect(sim.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT current_capital, 
               (SELECT COUNT(*) FROM trades_log WHERE portfolio_id = ?)
        FROM portfolios WHERE id = ?
    ''', (pid, pid))
    final, trades = cursor.fetchone()
    conn.close()
    
    return_pct = ((final - 10000) / 10000) * 100
    results.append((buy_thresh, sell_thresh, return_pct, trades))
    print(f"  ✅ {name}: {return_pct:+.2f}% ({trades} trades)\n")

print("\n" + "="*70)
print("📊 THRESHOLD COMPARISON")
print("="*70)
print(f"{'BUY':>6} {'SELL':>6} {'Return':>10} {'Trades':>8} {'$/Trade':>12}")
print("-"*70)

for buy, sell, ret, trades in results:
    dollars_per_trade = (ret * 100) / trades if trades > 0 else 0
    print(f"{buy:>6.1f} {sell:>6.1f} {ret:>9.2f}% {trades:>8} ${dollars_per_trade:>10.2f}")

print("\n🏆 Best Configuration:")
best = max(results, key=lambda x: x[2])  # Max return
print(f"BUY={best[0]}, SELL={best[1]} → {best[2]:+.2f}% ({best[3]} trades)")

print("\n✅ Threshold optimization complete!")
