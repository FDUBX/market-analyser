#!/usr/bin/env python3
"""
Market Analyzer - Main analysis engine
Fetches data, calculates indicators, and generates trading signals
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import argparse
import os

# Import cache if available
try:
    from data_cache import DataCache
    USE_CACHE = True
except ImportError:
    USE_CACHE = False

class MarketAnalyzer:
    def __init__(self, use_cache=True):
        self.weights = {
            'technical': 0.4,
            'fundamental': 0.4,
            'sentiment': 0.2
        }
        self.cache = DataCache() if USE_CACHE and use_cache else None
    
    def analyze_stock(self, ticker):
        """Analyze a stock and return comprehensive data"""
        try:
            # Use cache if available
            if self.cache:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                hist = self.cache.get_cached_data(ticker, start_date, end_date)
                info = self.cache.get_cached_info(ticker)
            else:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1y")
                info = stock.info
            
            if hist.empty:
                return {"error": f"No data for {ticker}"}
            
            # Calculate scores
            technical_score = self._calculate_technical_score(hist)
            fundamental_score = self._calculate_fundamental_score(info)
            sentiment_score = self._calculate_sentiment_score(hist)
            
            # Weighted total score
            total_score = (
                technical_score * self.weights['technical'] +
                fundamental_score * self.weights['fundamental'] +
                sentiment_score * self.weights['sentiment']
            )
            
            # Generate signal
            signal = self._generate_signal(total_score)
            
            # Current price
            current_price = hist['Close'].iloc[-1]
            
            # Price targets
            targets = self._calculate_targets(current_price, total_score)
            
            return {
                "ticker": ticker,
                "timestamp": datetime.now().isoformat(),
                "current_price": round(current_price, 2),
                "scores": {
                    "total": round(total_score, 2),
                    "technical": round(technical_score, 2),
                    "fundamental": round(fundamental_score, 2),
                    "sentiment": round(sentiment_score, 2)
                },
                "signal": signal,
                "targets": targets,
                "indicators": self._get_indicators(hist, info)
            }
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    def _calculate_technical_score(self, hist):
        """Calculate technical analysis score (0-10)"""
        scores = []
        
        # RSI (Relative Strength Index)
        rsi = self._calculate_rsi(hist['Close'])
        if rsi < 30:  # Oversold
            scores.append(8)
        elif rsi > 70:  # Overbought
            scores.append(2)
        else:
            # Normalize: RSI 30-70 -> Score 4-6
            scores.append(4 + (rsi - 30) / 20)
        
        # MACD
        macd_signal = self._calculate_macd(hist['Close'])
        scores.append(macd_signal)
        
        # Bollinger Bands
        bb_signal = self._calculate_bollinger(hist['Close'])
        scores.append(bb_signal)
        
        # Trend (SMA crossover)
        trend_signal = self._calculate_trend(hist['Close'])
        scores.append(trend_signal)
        
        # Volume analysis
        volume_signal = self._calculate_volume_signal(hist)
        scores.append(volume_signal)
        
        return np.mean(scores)
    
    def _calculate_fundamental_score(self, info):
        """Calculate fundamental analysis score (0-10)"""
        scores = []
        
        # P/E Ratio (lower is better, generally)
        pe = info.get('trailingPE', None)
        if pe:
            if pe < 15:
                scores.append(8)
            elif pe < 25:
                scores.append(6)
            elif pe < 35:
                scores.append(4)
            else:
                scores.append(2)
        
        # P/B Ratio
        pb = info.get('priceToBook', None)
        if pb:
            if pb < 1:
                scores.append(9)
            elif pb < 3:
                scores.append(7)
            elif pb < 5:
                scores.append(5)
            else:
                scores.append(3)
        
        # Profit Margin
        margin = info.get('profitMargins', None)
        if margin:
            if margin > 0.20:
                scores.append(8)
            elif margin > 0.10:
                scores.append(6)
            elif margin > 0:
                scores.append(4)
            else:
                scores.append(2)
        
        # Debt to Equity
        debt_to_equity = info.get('debtToEquity', None)
        if debt_to_equity is not None:
            if debt_to_equity < 50:
                scores.append(8)
            elif debt_to_equity < 100:
                scores.append(6)
            elif debt_to_equity < 200:
                scores.append(4)
            else:
                scores.append(2)
        
        # Revenue Growth
        revenue_growth = info.get('revenueGrowth', None)
        if revenue_growth:
            if revenue_growth > 0.20:
                scores.append(9)
            elif revenue_growth > 0.10:
                scores.append(7)
            elif revenue_growth > 0:
                scores.append(5)
            else:
                scores.append(3)
        
        return np.mean(scores) if scores else 5.0
    
    def _calculate_sentiment_score(self, hist):
        """Calculate market sentiment score based on price momentum"""
        # Simple momentum-based sentiment
        # In future: integrate news sentiment API
        
        # 30-day momentum
        returns_30d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-30] - 1) if len(hist) >= 30 else 0
        
        # Volume trend
        recent_vol = hist['Volume'].iloc[-5:].mean()
        avg_vol = hist['Volume'].mean()
        vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
        
        # Score calculation
        momentum_score = 5 + (returns_30d * 20)  # Convert % to score points
        momentum_score = max(0, min(10, momentum_score))
        
        volume_score = 5 + ((vol_ratio - 1) * 5)
        volume_score = max(0, min(10, volume_score))
        
        return np.mean([momentum_score, volume_score])
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _calculate_macd(self, prices):
        """Calculate MACD signal (0-10 score)"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        # Bullish if MACD > signal
        if macd.iloc[-1] > signal.iloc[-1]:
            return 7
        else:
            return 3
    
    def _calculate_bollinger(self, prices, period=20):
        """Calculate Bollinger Bands signal"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        
        current = prices.iloc[-1]
        upper_val = upper.iloc[-1]
        lower_val = lower.iloc[-1]
        
        # Near lower band = oversold = buy signal
        if current < lower_val:
            return 8
        elif current > upper_val:
            return 2
        else:
            # Normalize position within bands
            position = (current - lower_val) / (upper_val - lower_val)
            return 5 - (position - 0.5) * 6  # Invert: lower = better
    
    def _calculate_trend(self, prices):
        """Calculate trend using SMA crossover"""
        sma_50 = prices.rolling(window=50).mean().iloc[-1]
        sma_200 = prices.rolling(window=200).mean().iloc[-1] if len(prices) >= 200 else sma_50
        
        if sma_50 > sma_200:  # Bullish trend
            return 7
        else:  # Bearish trend
            return 3
    
    def _calculate_volume_signal(self, hist):
        """Analyze volume trends"""
        recent_vol = hist['Volume'].iloc[-5:].mean()
        avg_vol = hist['Volume'].iloc[-60:].mean()
        
        if recent_vol > avg_vol * 1.5:  # High volume
            # Check if price is rising or falling
            price_change = hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1
            if price_change > 0:
                return 7  # High volume + rising = bullish
            else:
                return 3  # High volume + falling = bearish
        else:
            return 5  # Normal volume
    
    def _generate_signal(self, score):
        """Generate trading signal based on score"""
        if score >= 7:
            return "BUY"
        elif score <= 3:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_targets(self, current_price, score):
        """Calculate price targets based on score"""
        if score >= 7:
            # Bullish: set upside targets
            return {
                "target": round(current_price * 1.15, 2),
                "stop_loss": round(current_price * 0.95, 2)
            }
        elif score <= 3:
            # Bearish: set downside protection
            return {
                "target": round(current_price * 0.90, 2),
                "stop_loss": round(current_price * 1.05, 2)
            }
        else:
            # Neutral
            return {
                "target": round(current_price * 1.05, 2),
                "stop_loss": round(current_price * 0.95, 2)
            }
    
    def _get_indicators(self, hist, info):
        """Get detailed indicator values"""
        rsi = self._calculate_rsi(hist['Close'])
        
        return {
            "rsi": round(rsi, 2),
            "pe_ratio": info.get('trailingPE', None),
            "pb_ratio": info.get('priceToBook', None),
            "profit_margin": round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') else None,
            "debt_to_equity": info.get('debtToEquity', None),
            "revenue_growth": round(info.get('revenueGrowth', 0) * 100, 2) if info.get('revenueGrowth') else None,
            "52w_high": info.get('fiftyTwoWeekHigh', None),
            "52w_low": info.get('fiftyTwoWeekLow', None)
        }


def main():
    parser = argparse.ArgumentParser(description='Market Analyzer')
    parser.add_argument('command', choices=['analyze', 'watch'], help='Command to execute')
    parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')
    parser.add_argument('--output', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--interval', default='5m', help='Watch interval (e.g., 5m, 1h)')
    
    args = parser.parse_args()
    
    analyzer = MarketAnalyzer()
    
    if args.command == 'analyze':
        results = []
        for ticker in args.tickers:
            result = analyzer.analyze_stock(ticker.upper())
            results.append(result)
            
            if args.output == 'text' and 'error' not in result:
                print(f"\n{'='*60}")
                print(f"📊 {result['ticker']} - ${result['current_price']}")
                print(f"{'='*60}")
                print(f"Total Score: {result['scores']['total']}/10")
                print(f"  Technical:    {result['scores']['technical']}/10")
                print(f"  Fundamental:  {result['scores']['fundamental']}/10")
                print(f"  Sentiment:    {result['scores']['sentiment']}/10")
                print(f"\nSignal: {result['signal']}")
                print(f"Target: ${result['targets']['target']}")
                print(f"Stop Loss: ${result['targets']['stop_loss']}")
                print(f"\nKey Indicators:")
                for key, value in result['indicators'].items():
                    if value is not None:
                        print(f"  {key}: {value}")
            elif 'error' in result:
                print(f"\n❌ Error analyzing {result['ticker']}: {result['error']}")
        
        if args.output == 'json':
            print(json.dumps(results, indent=2))
    
    elif args.command == 'watch':
        print(f"Watching {', '.join(args.tickers)} (interval: {args.interval})")
        print("Press Ctrl+C to stop\n")
        # TODO: Implement continuous monitoring
        print("Watch mode not yet implemented. Use 'analyze' for now.")


if __name__ == '__main__':
    main()
