#!/usr/bin/env python3
"""
Backtesting Engine - Test strategy performance on historical data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import argparse
from analyzer import MarketAnalyzer


class Backtester:
    def __init__(self, initial_capital=10000, position_size=0.2, stop_loss=0.05, take_profit=0.15):
        self.initial_capital = initial_capital
        self.position_size = position_size  # Fraction of capital per position
        self.stop_loss = stop_loss  # 5% stop loss
        self.take_profit = take_profit  # 15% take profit
        self.analyzer = MarketAnalyzer()
    
    def backtest_stock(self, ticker, period='2y'):
        """Backtest strategy on a single stock"""
        print(f"\n🔄 Backtesting {ticker} over {period}...")
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return {"error": f"No data for {ticker}"}
            
            # Simulate trading
            trades = []
            capital = self.initial_capital
            position = None
            
            # Iterate through historical data (skip first 200 days for indicators)
            for i in range(200, len(hist)):
                current_date = hist.index[i]
                current_price = hist['Close'].iloc[i]
                
                # Get historical data up to current point
                hist_slice = hist.iloc[:i+1]
                
                # Calculate score (simplified - using only technical for speed)
                score = self._calculate_score_at_date(hist_slice)
                
                # Trading logic
                if position is None:
                    # No position - check for buy signal
                    if score >= 7:  # Buy threshold
                        shares = int((capital * self.position_size) / current_price)
                        if shares > 0:
                            position = {
                                'entry_date': current_date,
                                'entry_price': current_price,
                                'shares': shares,
                                'capital_invested': shares * current_price
                            }
                            capital -= position['capital_invested']
                else:
                    # Have position - check exit conditions
                    pnl_pct = (current_price - position['entry_price']) / position['entry_price']
                    
                    # Exit conditions
                    should_exit = False
                    exit_reason = ''
                    
                    if pnl_pct <= -self.stop_loss:
                        should_exit = True
                        exit_reason = 'STOP_LOSS'
                    elif pnl_pct >= self.take_profit:
                        should_exit = True
                        exit_reason = 'TAKE_PROFIT'
                    elif score <= 3:  # Sell signal
                        should_exit = True
                        exit_reason = 'SELL_SIGNAL'
                    
                    if should_exit:
                        # Close position
                        exit_value = position['shares'] * current_price
                        capital += exit_value
                        
                        pnl = exit_value - position['capital_invested']
                        pnl_pct = (pnl / position['capital_invested']) * 100
                        
                        trades.append({
                            'entry_date': position['entry_date'].strftime('%Y-%m-%d'),
                            'exit_date': current_date.strftime('%Y-%m-%d'),
                            'entry_price': round(position['entry_price'], 2),
                            'exit_price': round(current_price, 2),
                            'shares': position['shares'],
                            'pnl': round(pnl, 2),
                            'pnl_pct': round(pnl_pct, 2),
                            'reason': exit_reason
                        })
                        
                        position = None
            
            # Close any open position at end
            if position:
                current_price = hist['Close'].iloc[-1]
                exit_value = position['shares'] * current_price
                capital += exit_value
                
                pnl = exit_value - position['capital_invested']
                pnl_pct = (pnl / position['capital_invested']) * 100
                
                trades.append({
                    'entry_date': position['entry_date'].strftime('%Y-%m-%d'),
                    'exit_date': hist.index[-1].strftime('%Y-%m-%d'),
                    'entry_price': round(position['entry_price'], 2),
                    'exit_price': round(current_price, 2),
                    'shares': position['shares'],
                    'pnl': round(pnl, 2),
                    'pnl_pct': round(pnl_pct, 2),
                    'reason': 'END_OF_PERIOD'
                })
            
            # Calculate metrics
            total_return = capital - self.initial_capital
            total_return_pct = (total_return / self.initial_capital) * 100
            
            winning_trades = [t for t in trades if t['pnl'] > 0]
            losing_trades = [t for t in trades if t['pnl'] <= 0]
            
            win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0
            
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
            
            # Buy & Hold comparison
            buy_hold_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[200]) / hist['Close'].iloc[200]) * 100
            
            return {
                'ticker': ticker,
                'period': period,
                'initial_capital': self.initial_capital,
                'final_capital': round(capital, 2),
                'total_return': round(total_return, 2),
                'total_return_pct': round(total_return_pct, 2),
                'num_trades': len(trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': round(win_rate, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'buy_hold_return_pct': round(buy_hold_return, 2),
                'vs_buy_hold': round(total_return_pct - buy_hold_return, 2),
                'trades': trades
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    def _calculate_score_at_date(self, hist_slice):
        """Calculate technical score at specific point in time"""
        # Simplified scoring for backtesting (only technical)
        scores = []
        
        # RSI
        rsi = self._calculate_rsi(hist_slice['Close'])
        if rsi < 30:
            scores.append(8)
        elif rsi > 70:
            scores.append(2)
        else:
            scores.append(4 + (rsi - 30) / 20)
        
        # MACD
        exp1 = hist_slice['Close'].ewm(span=12, adjust=False).mean()
        exp2 = hist_slice['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        if macd.iloc[-1] > signal.iloc[-1]:
            scores.append(7)
        else:
            scores.append(3)
        
        # Trend
        if len(hist_slice) >= 200:
            sma_50 = hist_slice['Close'].rolling(window=50).mean().iloc[-1]
            sma_200 = hist_slice['Close'].rolling(window=200).mean().iloc[-1]
            
            if sma_50 > sma_200:
                scores.append(7)
            else:
                scores.append(3)
        
        return np.mean(scores)
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]


def main():
    parser = argparse.ArgumentParser(description='Backtest Market Analyzer Strategy')
    parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')
    parser.add_argument('--period', default='2y', help='Backtest period (e.g., 1y, 2y, 5y)')
    parser.add_argument('--capital', type=float, default=10000, help='Initial capital')
    parser.add_argument('--position-size', type=float, default=0.2, help='Position size (fraction)')
    parser.add_argument('--stop-loss', type=float, default=0.05, help='Stop loss (fraction)')
    parser.add_argument('--take-profit', type=float, default=0.15, help='Take profit (fraction)')
    parser.add_argument('--output', choices=['json', 'text'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    backtester = Backtester(
        initial_capital=args.capital,
        position_size=args.position_size,
        stop_loss=args.stop_loss,
        take_profit=args.take_profit
    )
    
    results = []
    for ticker in args.tickers:
        result = backtester.backtest_stock(ticker.upper(), args.period)
        results.append(result)
        
        if args.output == 'text' and 'error' not in result:
            print(f"\n{'='*70}")
            print(f"📈 BACKTEST RESULTS - {result['ticker']} ({result['period']})")
            print(f"{'='*70}")
            print(f"Initial Capital:    ${result['initial_capital']:,.2f}")
            print(f"Final Capital:      ${result['final_capital']:,.2f}")
            print(f"Total Return:       ${result['total_return']:,.2f} ({result['total_return_pct']:+.2f}%)")
            print(f"\nStrategy vs Buy & Hold:")
            print(f"  Strategy Return:  {result['total_return_pct']:+.2f}%")
            print(f"  Buy & Hold:       {result['buy_hold_return_pct']:+.2f}%")
            print(f"  Difference:       {result['vs_buy_hold']:+.2f}%")
            print(f"\nTrade Statistics:")
            print(f"  Total Trades:     {result['num_trades']}")
            print(f"  Winning Trades:   {result['winning_trades']}")
            print(f"  Losing Trades:    {result['losing_trades']}")
            print(f"  Win Rate:         {result['win_rate']:.2f}%")
            print(f"  Avg Win:          ${result['avg_win']:,.2f}")
            print(f"  Avg Loss:         ${result['avg_loss']:,.2f}")
            
            if result['trades']:
                print(f"\nRecent Trades (last 5):")
                for trade in result['trades'][-5:]:
                    print(f"  {trade['entry_date']} → {trade['exit_date']}: "
                          f"${trade['entry_price']} → ${trade['exit_price']} "
                          f"({trade['pnl_pct']:+.2f}%) - {trade['reason']}")
        elif 'error' in result:
            print(f"\n❌ Error backtesting {result['ticker']}: {result['error']}")
    
    if args.output == 'json':
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
