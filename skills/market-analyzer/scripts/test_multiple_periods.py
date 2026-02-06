#!/usr/bin/env python3
"""
Test v2.0 on multiple periods
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from portfolio_sim import PortfolioSimulator
import json

def main():
    sim = PortfolioSimulator()
    
    test_periods = [
        ("2023 Full Year", "2023-01-01", "2023-12-31"),
        ("2024 H1", "2024-01-01", "2024-06-30"),
        ("2024 H2", "2024-07-01", "2024-12-31"),
        ("2025 YTD", "2025-01-01", "2026-02-05"),
        ("18 months", "2024-07-01", "2025-12-31"),
    ]
    
    print("\n🔬 Creating test portfolios for multiple periods...\n")
    
    created_ids = []
    for name, start, end in test_periods:
        try:
            result = sim.create_portfolio(f"v2.0 {name}", 10000, start)
            print(f"DEBUG: Result = {result}")
            pid = result['portfolio_id']
            created_ids.append((pid, name, end))
            print(f"✅ Created: v2.0 {name} (ID: {pid})")
        except Exception as e:
            print(f"❌ Error creating {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🚀 Running simulations...\n")
    
    for pid, name, end_date in created_ids:
        print(f"⏳ Running: {name}...")
        sim.run_simulation(pid, end_date=end_date)
    
    print("\n✅ All simulations complete!")
    print("\nRun: python3 scripts/compare_versions.py to see results")

if __name__ == '__main__':
    main()
