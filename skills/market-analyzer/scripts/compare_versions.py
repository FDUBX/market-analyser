#!/usr/bin/env python3
"""
Compare performance of different versions/configurations
"""

import sqlite3
import sys

def compare_portfolios(db_path='portfolio_sim.db'):
    """Compare all portfolios"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, initial_capital, current_capital, start_date, end_date,
               (SELECT COUNT(*) FROM trades_log WHERE portfolio_id = p.id) as num_trades
        FROM portfolios p
        ORDER BY start_date, name
    ''')
    
    portfolios = cursor.fetchall()
    
    print("\n" + "="*100)
    print(f"{'Portfolio':<30} {'Period':<25} {'Initial':>12} {'Final':>12} {'Return':>10} {'Trades':>8}")
    print("="*100)
    
    results_by_year = {}
    
    for p in portfolios:
        pid, name, initial, current, start, end, trades = p
        return_pct = ((current - initial) / initial) * 100
        
        period = f"{start} → {end or 'now'}"
        year = start[:4]
        
        if year not in results_by_year:
            results_by_year[year] = []
        
        results_by_year[year].append({
            'name': name,
            'return': return_pct,
            'trades': trades,
            'final': current
        })
        
        color = '\033[92m' if return_pct > 0 else '\033[91m'
        reset = '\033[0m'
        
        print(f"{name:<30} {period:<25} ${initial:>11,.0f} ${current:>11,.0f} {color}{return_pct:>9.2f}%{reset} {trades:>8}")
    
    # Summary by year
    print("\n" + "="*100)
    print("📊 SUMMARY BY YEAR")
    print("="*100)
    
    for year in sorted(results_by_year.keys()):
        print(f"\n{year}:")
        portfolios_year = results_by_year[year]
        
        # Find best
        best = max(portfolios_year, key=lambda x: x['return'])
        print(f"  🏆 Best: {best['name']:<25} → {best['return']:+.2f}% ({best['trades']} trades)")
        
        # Average
        avg_return = sum(p['return'] for p in portfolios_year) / len(portfolios_year)
        avg_trades = sum(p['trades'] for p in portfolios_year) / len(portfolios_year)
        print(f"  📈 Average: {avg_return:+.2f}% ({avg_trades:.0f} trades)")
    
    conn.close()

if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    compare_portfolios()
