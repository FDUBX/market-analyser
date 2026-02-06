#!/usr/bin/env python3
"""Validate v2.1 optimal config (5.5/4.5) on multiple periods"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from portfolio_sim import PortfolioSimulator

sim = PortfolioSimulator()

# Optimal config from threshold testing
optimal_config = {
    "buy_threshold": 5.5,
    "sell_threshold": 4.5,
    "position_size": 0.20,
    "stop_loss": 0.05,
    "take_profit": 0.18,
    "weights": {"technical": 0.4, "fundamental": 0.4, "sentiment": 0.2}
}

test_periods = [
    ("v2.1 Opt 2023", "2023-01-01", "2023-12-31"),
    ("v2.1 Opt 2024", "2024-01-01", "2024-12-31"),
    ("v2.1 Opt 2025", "2025-01-01", "2025-12-31"),
]

print("\n🔬 Validating v2.1 Optimal Config (BUY=5.5, SELL=4.5)\n")

results = []

for name, start, end in test_periods:
    print(f"Testing {name} ({start} → {end})...")
    
    result = sim.create_portfolio(name, 10000, start, config=optimal_config)
    pid = result['portfolio_id']
    
    sim.run_simulation(pid, end_date=end)
    
    # Get results
    import sqlite3
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
    results.append((name, return_pct, trades))
    print(f"  ✅ {return_pct:+.2f}% ({trades} trades)\n")

print("\n" + "="*70)
print("📊 V2.1 VALIDATION RESULTS")
print("="*70)
print(f"{'Period':<20} {'Return':>12} {'Trades':>10}")
print("-"*70)

total_return = 0
total_trades = 0
for name, ret, trades in results:
    period = name.replace("v2.1 Opt ", "")
    print(f"{period:<20} {ret:>11.2f}% {trades:>10}")
    total_return += ret
    total_trades += trades

avg_return = total_return / len(results)
print("-"*70)
print(f"{'Average':<20} {avg_return:>11.2f}% {total_trades:>10}")

print("\n✅ Validation complete!")
