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
        """Calculate technical analysis score (0-10) - v2.1 WEIGHTED indicators"""
        
        # Core indicators (proven, higher weight)
        rsi = self._calculate_rsi(hist['Close'])
        if rsi < 30:
            rsi_score = 8
        elif rsi > 70:
            rsi_score = 2
        else:
            rsi_score = 4 + (rsi - 30) / 20
        
        macd_score = self._calculate_macd(hist['Close'])
        bb_score = self._calculate_bollinger(hist['Close'])
        trend_score = self._calculate_trend(hist['Close'])
        volume_score = self._calculate_volume_signal(hist)
        
        # New indicators (supplementary, lower weight)
        adx_score = self._calculate_adx_score(hist) or 5  # Default to neutral
        willr_score = self._calculate_williams_r_score(hist) or 5
        obv_score = self._calculate_obv_score(hist) or 5
        pos_52w_score = self._calculate_52w_position_score(hist) or 5
        
        # v2.1: WEIGHTED SCORING
        # Core indicators get 80%, new ones get 20%
        weighted_score = (
            rsi_score * 0.20 +        # 20% - Most reliable momentum
            macd_score * 0.18 +       # 18% - Trend confirmation
            bb_score * 0.15 +         # 15% - Volatility/extremes
            trend_score * 0.15 +      # 15% - SMA crossover
            volume_score * 0.12 +     # 12% - Volume confirmation
            adx_score * 0.08 +        #  8% - Trend strength (new)
            willr_score * 0.06 +      #  6% - Momentum complement (new)
            obv_score * 0.03 +        #  3% - Volume trend (new)
            pos_52w_score * 0.03      #  3% - Support/resistance (new)
        )
        
        return weighted_score
    
    def _calculate_fundamental_score(self, info):
        """Calculate fundamental analysis score (0-10) - diversified indicators"""
        scores = []
        
        # P/E Ratio
        pe = info.get('trailingPE', None)
        if pe and pe > 0:
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
        if pb is not None and pb > 0:
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
        if margin is not None and margin > 0:
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
        if revenue_growth is not None:
            if revenue_growth > 0.20:
                scores.append(9)
            elif revenue_growth > 0.10:
                scores.append(7)
            elif revenue_growth > 0:
                scores.append(5)
            else:
                scores.append(3)
        
        # ROE (Return on Equity)
        roe_score = self._score_roe(info)
        if roe_score is not None:
            scores.append(roe_score)
        
        # Free Cash Flow yield (FCF / market cap proxy: positive FCF = good)
        fcf_score = self._score_fcf(info)
        if fcf_score is not None:
            scores.append(fcf_score)
        
        # Current Ratio (liquidity)
        cr_score = self._score_current_ratio(info)
        if cr_score is not None:
            scores.append(cr_score)
        
        return np.mean(scores) if scores else 5.0
    
    def _calculate_sentiment_score(self, hist):
        """Calculate market sentiment score - diversified (momentum, volume, range, volatility)"""
        scores = []
        
        # 30-day momentum
        returns_30d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-30] - 1) if len(hist) >= 30 else 0
        momentum_score = 5 + (returns_30d * 20)
        momentum_score = max(0, min(10, momentum_score))
        scores.append(momentum_score)
        
        # 5-day momentum (short-term vs 30d = divergence possible)
        returns_5d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1) if len(hist) >= 5 else 0
        momentum_5d_score = 5 + (returns_5d * 30)
        momentum_5d_score = max(0, min(10, momentum_5d_score))
        scores.append(momentum_5d_score)
        
        # Volume trend
        recent_vol = hist['Volume'].iloc[-5:].mean()
        avg_vol = hist['Volume'].mean()
        vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
        volume_score = 5 + ((vol_ratio - 1) * 5)
        volume_score = max(0, min(10, volume_score))
        scores.append(volume_score)
        
        # 52-week range position (price near high = bullish sentiment)
        pos = self._score_52w_range_sentiment(hist)
        if pos is not None:
            scores.append(pos)
        
        # Volatility (low vol = more confidence / less fear; high vol = uncertainty)
        vol_score = self._score_volatility_sentiment(hist)
        if vol_score is not None:
            scores.append(vol_score)
        
        return np.mean(scores)
    
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
    
    def _calculate_adx_score(self, hist, period=14):
        """ADX (Average Directional Index) - trend strength. Strong trend -> higher score."""
        if len(hist) < period * 2:
            return None
        high, low, close = hist['High'], hist['Low'], hist['Close']
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean().iloc[-1]
        # ADX 0-25 weak, 25-50 strong, 50+ very strong. Score 0-10: we want strong trend = clearer signal
        if pd.isna(adx):
            return None
        adx_score = 3 + (adx / 50) * 7  # 25 -> ~6.5, 50 -> 10
        return max(0, min(10, adx_score))
    
    def _calculate_williams_r_score(self, hist, period=14):
        """Williams %R: oversold (< -80) = buy, overbought (> -20) = sell. Complement to RSI."""
        if len(hist) < period:
            return None
        high = hist['High'].rolling(period).max()
        low = hist['Low'].rolling(period).min()
        close = hist['Close']
        willr = -100 * (high - close) / (high - low)
        willr = willr.replace([np.inf, -np.inf], np.nan).dropna()
        if willr.empty:
            return None
        w = willr.iloc[-1]
        if w < -80:
            return 8   # oversold
        elif w > -20:
            return 2   # overbought
        else:
            return 5 + (w + 50) / 10  # -50 -> 5, linear in between
    
    def _calculate_obv_score(self, hist):
        """On-Balance Volume trend: OBV rising with price = bullish."""
        if len(hist) < 20:
            return None
        close, vol = hist['Close'], hist['Volume']
        obv = (np.sign(close.diff()) * vol).fillna(0).cumsum()
        obv_recent = obv.iloc[-5:].mean()
        obv_older = obv.iloc[-20:-5].mean()
        price_up = close.iloc[-1] > close.iloc[-5]
        obv_up = obv_recent > obv_older
        if price_up and obv_up:
            return 7
        elif not price_up and not obv_up:
            return 3
        return 5
    
    def _calculate_52w_position_score(self, hist):
        """Price position in 52-week range. Near high = bullish, near low = bearish."""
        if len(hist) < 20:
            return None
        high_52 = hist['High'].iloc[-252:].max() if len(hist) >= 252 else hist['High'].max()
        low_52 = hist['Low'].iloc[-252:].min() if len(hist) >= 252 else hist['Low'].min()
        current = hist['Close'].iloc[-1]
        if high_52 <= low_52:
            return 5
        pct = (current - low_52) / (high_52 - low_52)  # 0 = at low, 1 = at high
        return pct * 8 + 1  # 1-9 scale
    
    def _score_roe(self, info):
        """Return on Equity: higher = better (quality)."""
        roe = info.get('returnOnEquity', None)
        if roe is None:
            return None
        if roe > 0.20:
            return 9
        elif roe > 0.10:
            return 7
        elif roe > 0:
            return 5
        return 2
    
    def _score_fcf(self, info):
        """Free cash flow: positive = healthy. Uses FCF / revenue proxy if no market cap."""
        fcf = info.get('freeCashflow')
        rev = info.get('totalRevenue')
        if fcf is None:
            return None
        if rev and rev > 0:
            fcf_ratio = fcf / rev
            if fcf_ratio > 0.15:
                return 8
            elif fcf_ratio > 0.05:
                return 6
            elif fcf_ratio > 0:
                return 5
            return 3
        return 7 if fcf > 0 else 3
    
    def _score_current_ratio(self, info):
        """Current ratio (liquidity): > 1.5 = healthy."""
        cr = info.get('currentRatio', None)
        if cr is None or cr <= 0:
            return None
        if cr >= 2:
            return 8
        elif cr >= 1.5:
            return 6
        elif cr >= 1:
            return 4
        return 2
    
    def _score_52w_range_sentiment(self, hist):
        """Sentiment: where price sits in 52w range (same as technical but sentiment angle)."""
        return self._calculate_52w_position_score(hist)
    
    def _score_volatility_sentiment(self, hist, window=20):
        """Low recent volatility = more confidence; high vol = uncertainty. Inverse vol -> score."""
        if len(hist) < window:
            return None
        ret = hist['Close'].pct_change().iloc[-window:]
        vol = ret.std()
        if vol is None or vol == 0 or pd.isna(vol):
            return 5
        # Annualized vol proxy: low vol -> high score (e.g. 0.15 -> 6, 0.40 -> 3)
        vol_annual = vol * (252 ** 0.5)
        if vol_annual < 0.15:
            return 8
        elif vol_annual < 0.25:
            return 6
        elif vol_annual < 0.40:
            return 4
        return 2
    
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
        """Get detailed indicator values (technical, fundamental, sentiment)"""
        rsi = self._calculate_rsi(hist['Close'])
        # Technical
        high_52 = hist['High'].iloc[-252:].max() if len(hist) >= 252 else hist['High'].max()
        low_52 = hist['Low'].iloc[-252:].min() if len(hist) >= 252 else hist['Low'].min()
        close = hist['Close'].iloc[-1]
        pos_52w = (close - low_52) / (high_52 - low_52) * 100 if high_52 > low_52 else None
        ret_20 = hist['Close'].pct_change().iloc[-20:]
        vol_20 = ret_20.std() * (252 ** 0.5) * 100 if len(ret_20) >= 20 else None  # annualized % 
        willr = None
        if len(hist) >= 14:
            h, l, c = hist['High'].rolling(14).max(), hist['Low'].rolling(14).min(), hist['Close']
            w = -100 * (h - c) / (h - l)
            willr = round(w.iloc[-1], 2) if not (pd.isna(w.iloc[-1]) or np.isinf(w.iloc[-1])) else None
        
        return {
            "rsi": round(rsi, 2),
            "williams_r": willr,
            "52w_position_pct": round(pos_52w, 2) if pos_52w is not None else None,
            "volatility_20d_annual_pct": round(vol_20, 2) if vol_20 is not None else None,
            "pe_ratio": info.get('trailingPE', None),
            "pb_ratio": info.get('priceToBook', None),
            "profit_margin": round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') else None,
            "debt_to_equity": info.get('debtToEquity', None),
            "revenue_growth": round(info.get('revenueGrowth', 0) * 100, 2) if info.get('revenueGrowth') is not None else None,
            "roe_pct": round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') is not None else None,
            "free_cash_flow": info.get('freeCashflow', None),
            "current_ratio": info.get('currentRatio', None),
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
