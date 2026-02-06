#!/usr/bin/env python3
"""Quick multi-period test"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from portfolio_sim import PortfolioSimulator

sim = PortfolioSimulator()

tests = [
    ("v2.0 2023", "2023-01-01", "2023-12-31"),
]

for name, start, end in tests:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}\n")
    
    result = sim.create_portfolio(name, 10000, start)
    pid = result['portfolio_id']
    print(f"Created portfolio ID: {pid}")
    
    sim.run_simulation(pid, end_date=end)
    
    # Get results
    import sqlite3
    conn = sqlite3.connect(sim.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT current_capital FROM portfolios WHERE id = ?', (pid,))
    final = cursor.fetchone()[0]
    conn.close()
    
    return_pct = ((final - 10000) / 10000) * 100
    print(f"\n✅ {name}: {return_pct:+.2f}%")

print("\n✅ All tests complete!")
