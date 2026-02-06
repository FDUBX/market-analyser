#!/usr/bin/env python3
"""
Strategy Optimizer - Find optimal thresholds and weights
"""

import pandas as pd
import numpy as np
from itertools import product
from backtest import Backtester
from datetime import datetime
import json

class StrategyOptimizer:
    def __init__(self):
        self.backtester = Backtester()
    
    def optimize_thresholds(self, ticker, period='2y', 
                           buy_range=(5.0, 7.5, 0.5),
                           sell_range=(3.0, 5.0, 0.5)):
        """Find optimal buy/sell thresholds"""
        
        print(f"\n🔍 Optimizing thresholds for {ticker} over {period}...")
        print(f"Buy range: {buy_range[0]}-{buy_range[1]} (step {buy_range[2]})")
        print(f"Sell range: {sell_range[0]}-{sell_range[1]} (step {sell_range[2]})\n")
        
        buy_thresholds = np.arange(buy_range[0], buy_range[1] + buy_range[2], buy_range[2])
        sell_thresholds = np.arange(sell_range[0], sell_range[1] + sell_range[2], sell_range[2])
        
        results = []
        best_return = -float('inf')
        best_config = None
        
        total_tests = len(buy_thresholds) * len(sell_thresholds)
        current = 0
        
        for buy_thresh in buy_thresholds:
            for sell_thresh in sell_thresholds:
                current += 1
                
                # Skip invalid combinations
                if sell_thresh >= buy_thresh:
                    continue
                
                print(f"Testing [{current}/{total_tests}]: BUY={buy_thresh:.1f}, SELL={sell_thresh:.1f}...", end='\r')
                
                # Temporarily modify thresholds (would need to pass to backtester)
                # For now, simplified version
                result = {
                    'buy_threshold': buy_thresh,
                    'sell_threshold': sell_thresh,
                    'return_pct': 0,  # Placeholder - need to run actual backtest
                    'win_rate': 0,
                    'num_trades': 0
                }
                
                results.append(result)
        
        print("\n")
        
        # Sort by return
        results.sort(key=lambda x: x['return_pct'], reverse=True)
        
        print("\n📊 Top 5 configurations:\n")
        for i, r in enumerate(results[:5], 1):
            print(f"{i}. BUY={r['buy_threshold']:.1f}, SELL={r['sell_threshold']:.1f} → "
                  f"Return: {r['return_pct']:+.2f}% | Trades: {r['num_trades']} | Win rate: {r['win_rate']:.1f}%")
        
        return results[0] if results else None
    
    def optimize_weights(self, ticker, period='2y'):
        """Find optimal weight combinations"""
        
        print(f"\n🔍 Optimizing weights for {ticker} over {period}...")
        
        # Test different weight combinations
        weight_configs = [
            {'technical': 0.6, 'fundamental': 0.3, 'sentiment': 0.1, 'name': 'Tech-Heavy'},
            {'technical': 0.4, 'fundamental': 0.4, 'sentiment': 0.2, 'name': 'Balanced'},
            {'technical': 0.3, 'fundamental': 0.5, 'sentiment': 0.2, 'name': 'Value'},
            {'technical': 0.5, 'fundamental': 0.3, 'sentiment': 0.2, 'name': 'Momentum'},
            {'technical': 0.7, 'fundamental': 0.2, 'sentiment': 0.1, 'name': 'Aggressive'},
        ]
        
        results = []
        
        for config in weight_configs:
            print(f"Testing {config['name']}: "
                  f"Tech={config['technical']:.0%}, "
                  f"Fund={config['fundamental']:.0%}, "
                  f"Sent={config['sentiment']:.0%}")
            
            # Would run backtest with these weights
            result = {
                'name': config['name'],
                'weights': config,
                'return_pct': 0,  # Placeholder
                'win_rate': 0,
                'sharpe_ratio': 0
            }
            
            results.append(result)
        
        results.sort(key=lambda x: x['return_pct'], reverse=True)
        
        print("\n📊 Weight comparison:\n")
        for r in results:
            print(f"{r['name']:15s} → Return: {r['return_pct']:+.2f}% | "
                  f"Win rate: {r['win_rate']:.1f}% | Sharpe: {r['sharpe_ratio']:.2f}")
        
        return results[0] if results else None
    
    def compare_strategies(self, tickers, period='1y'):
        """Compare multiple pre-defined strategies"""
        
        strategies = {
            'Conservative': {
                'buy_threshold': 7.0,
                'sell_threshold': 4.0,
                'weights': {'technical': 0.3, 'fundamental': 0.5, 'sentiment': 0.2},
                'stop_loss': 0.05,
                'take_profit': 0.10
            },
            'Balanced': {
                'buy_threshold': 6.0,
                'sell_threshold': 4.5,
                'weights': {'technical': 0.4, 'fundamental': 0.4, 'sentiment': 0.2},
                'stop_loss': 0.05,
                'take_profit': 0.15
            },
            'Aggressive': {
                'buy_threshold': 5.5,
                'sell_threshold': 5.0,
                'weights': {'technical': 0.6, 'fundamental': 0.3, 'sentiment': 0.1},
                'stop_loss': 0.07,
                'take_profit': 0.20
            },
            'Momentum': {
                'buy_threshold': 6.5,
                'sell_threshold': 4.0,
                'weights': {'technical': 0.7, 'fundamental': 0.2, 'sentiment': 0.1},
                'stop_loss': 0.04,
                'take_profit': 0.12
            }
        }
        
        print(f"\n📊 Comparing {len(strategies)} strategies on {len(tickers)} stocks over {period}\n")
        
        results = {}
        
        for strategy_name, config in strategies.items():
            print(f"\n{'='*60}")
            print(f"Strategy: {strategy_name}")
            print(f"{'='*60}")
            print(f"BUY: {config['buy_threshold']:.1f} | SELL: {config['sell_threshold']:.1f}")
            print(f"Weights: Tech={config['weights']['technical']:.0%}, "
                  f"Fund={config['weights']['fundamental']:.0%}, "
                  f"Sent={config['weights']['sentiment']:.0%}")
            print(f"Stop-loss: {config['stop_loss']:.0%} | Take-profit: {config['take_profit']:.0%}")
            
            strategy_results = {
                'config': config,
                'stocks': {},
                'avg_return': 0,
                'avg_win_rate': 0,
                'total_trades': 0
            }
            
            # Would test each ticker
            for ticker in tickers:
                # Placeholder
                strategy_results['stocks'][ticker] = {
                    'return_pct': 0,
                    'win_rate': 0,
                    'num_trades': 0
                }
            
            results[strategy_name] = strategy_results
        
        # Summary
        print(f"\n{'='*60}")
        print("📈 STRATEGY COMPARISON SUMMARY")
        print(f"{'='*60}\n")
        
        for strategy_name, data in results.items():
            print(f"{strategy_name:15s} → Avg Return: {data['avg_return']:+.2f}% | "
                  f"Avg Win Rate: {data['avg_win_rate']:.1f}% | "
                  f"Total Trades: {data['total_trades']}")
        
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Strategy Optimizer')
    parser.add_argument('command', choices=['thresholds', 'weights', 'compare'], help='Optimization type')
    parser.add_argument('--ticker', default='AAPL', help='Stock ticker')
    parser.add_argument('--tickers', nargs='+', help='Multiple tickers for comparison')
    parser.add_argument('--period', default='2y', help='Backtest period')
    
    args = parser.parse_args()
    
    optimizer = StrategyOptimizer()
    
    if args.command == 'thresholds':
        result = optimizer.optimize_thresholds(args.ticker, args.period)
        if result:
            print(f"\n✅ Optimal configuration:")
            print(f"BUY threshold: {result['buy_threshold']:.1f}")
            print(f"SELL threshold: {result['sell_threshold']:.1f}")
    
    elif args.command == 'weights':
        result = optimizer.optimize_weights(args.ticker, args.period)
        if result:
            print(f"\n✅ Best weight configuration: {result['name']}")
    
    elif args.command == 'compare':
        tickers = args.tickers or ['AAPL', 'MSFT', 'GOOGL']
        results = optimizer.compare_strategies(tickers, args.period)


if __name__ == '__main__':
    main()
