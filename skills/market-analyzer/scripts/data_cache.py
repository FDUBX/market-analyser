#!/usr/bin/env python3
"""
Data Cache - Local cache for Yahoo Finance data to avoid rate limits
"""

import yfinance as yf
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time

class DataCache:
    def __init__(self, db_path='data_cache.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Historical prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                cached_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ticker, date)
            )
        ''')
        
        # Stock info cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_info (
                ticker TEXT PRIMARY KEY,
                info_json TEXT,
                cached_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def fetch_and_cache(self, ticker, start_date, end_date, force_refresh=False):
        """Fetch data from Yahoo Finance and cache it"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if we already have this data
            if not force_refresh:
                cursor.execute('''
                    SELECT COUNT(*) FROM price_history 
                    WHERE ticker = ? AND date BETWEEN ? AND ?
                ''', (ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
                
                count = cursor.fetchone()[0]
                expected_days = (end_date - start_date).days
                
                # If we have most of the data, skip download
                if count > expected_days * 0.7:  # 70% threshold
                    return True
            
            # Download from Yahoo Finance
            print(f"  📥 Downloading {ticker}...")
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date + timedelta(days=1))
            
            if hist.empty:
                print(f"  ⚠️  No data for {ticker}")
                return False
            
            # Insert into cache
            for date, row in hist.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO price_history (ticker, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    date.strftime('%Y-%m-%d'),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume'])
                ))
            
            # Cache stock info
            info = stock.info
            import json
            cursor.execute('''
                INSERT OR REPLACE INTO stock_info (ticker, info_json)
                VALUES (?, ?)
            ''', (ticker, json.dumps(info)))
            
            conn.commit()
            print(f"  ✅ {ticker} cached ({len(hist)} days)")
            
            # Rate limit protection
            time.sleep(0.5)  # 500ms between requests
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error caching {ticker}: {e}")
            return False
        finally:
            conn.close()
    
    def get_cached_data(self, ticker, start_date, end_date):
        """Get cached historical data"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            query = '''
                SELECT date, open, high, low, close, volume
                FROM price_history
                WHERE ticker = ? AND date BETWEEN ? AND ?
                ORDER BY date
            '''
            
            df = pd.read_sql_query(
                query,
                conn,
                params=(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            )
            
            if df.empty:
                # If we have a last close before/on start_date, likely weekend/holiday → skip API (avoids "No data" spam)
                last_date, _ = self.get_last_close_before_or_on(ticker, start_date)
                if last_date is None:
                    # No data at all, try API
                    if self.fetch_and_cache(ticker, start_date, end_date):
                        df = pd.read_sql_query(query, conn, params=(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
                else:
                    # We have history; missing date is probably non-trading day, don't call API
                    pass
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            return df
            
        finally:
            conn.close()
    
    def get_last_close_before_or_on(self, ticker, as_of_date):
        """
        Return (date_str, close_price) for the last trading day on or before as_of_date.
        Used when market is closed (weekend, holiday) to avoid valuing positions at 0.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            as_str = as_of_date.strftime('%Y-%m-%d') if hasattr(as_of_date, 'strftime') else as_of_date
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, close FROM price_history
                WHERE ticker = ? AND date <= ?
                ORDER BY date DESC
                LIMIT 1
            ''', (ticker, as_str))
            row = cursor.fetchone()
            if row:
                return (row[0], float(row[1]))
            return (None, None)
        finally:
            conn.close()
    
    def get_cached_info(self, ticker):
        """Get cached stock info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT info_json FROM stock_info WHERE ticker = ?', (ticker,))
            row = cursor.fetchone()
            
            if row:
                import json
                return json.loads(row[0])
            else:
                # Try to fetch from API
                # FIX BUG-5: Catch specific Exception instead of bare except
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    cursor.execute('''
                        INSERT OR REPLACE INTO stock_info (ticker, info_json)
                        VALUES (?, ?)
                    ''', (ticker, json.dumps(info)))
                    conn.commit()
                    return info
                except Exception as e:
                    print(f"  ⚠️  Could not fetch info for {ticker}: {e}")
                    return {}
        finally:
            conn.close()
    
    def preload_universe(self, tickers, start_date, end_date):
        """Preload data for multiple tickers"""
        print(f"\n📥 Preloading data for {len(tickers)} tickers...")
        print(f"📅 Period: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}\n")
        
        success = 0
        failed = []
        
        for ticker in tickers:
            if self.fetch_and_cache(ticker, start_date, end_date):
                success += 1
            else:
                failed.append(ticker)
        
        print(f"\n✅ Preloaded {success}/{len(tickers)} tickers")
        if failed:
            print(f"❌ Failed: {', '.join(failed)}")
        
        return success, failed
    
    def clear_cache(self, ticker=None, older_than_days=None):
        """Clear cache (all or specific ticker or old data)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if ticker:
                cursor.execute('DELETE FROM price_history WHERE ticker = ?', (ticker,))
                cursor.execute('DELETE FROM stock_info WHERE ticker = ?', (ticker,))
                print(f"🗑️  Cleared cache for {ticker}")
            elif older_than_days:
                cutoff = (datetime.now() - timedelta(days=older_than_days)).strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('DELETE FROM price_history WHERE cached_at < ?', (cutoff,))
                cursor.execute('DELETE FROM stock_info WHERE cached_at < ?', (cutoff,))
                print(f"🗑️  Cleared cache older than {older_than_days} days")
            else:
                cursor.execute('DELETE FROM price_history')
                cursor.execute('DELETE FROM stock_info')
                print("🗑️  Cleared all cache")
            
            conn.commit()
        finally:
            conn.close()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(DISTINCT ticker) FROM price_history')
            num_tickers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM price_history')
            num_rows = cursor.fetchone()[0]
            
            cursor.execute('SELECT MIN(date), MAX(date) FROM price_history')
            date_range = cursor.fetchone()
            
            return {
                'tickers': num_tickers,
                'data_points': num_rows,
                'date_range': date_range
            }
        finally:
            conn.close()


def main():
    """CLI for cache management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Cache Manager')
    parser.add_argument('command', choices=['preload', 'stats', 'clear'], help='Command')
    parser.add_argument('--tickers', nargs='+', help='Ticker symbols')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--ticker', help='Specific ticker to clear')
    
    args = parser.parse_args()
    
    cache = DataCache()
    
    if args.command == 'preload':
        if not args.tickers or not args.start or not args.end:
            print("❌ --tickers, --start, and --end are required")
            return
        
        start = datetime.strptime(args.start, '%Y-%m-%d')
        end = datetime.strptime(args.end, '%Y-%m-%d')
        
        cache.preload_universe(args.tickers, start, end)
    
    elif args.command == 'stats':
        stats = cache.get_cache_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"Tickers cached: {stats['tickers']}")
        print(f"Data points: {stats['data_points']:,}")
        print(f"Date range: {stats['date_range'][0]} → {stats['date_range'][1]}")
    
    elif args.command == 'clear':
        if args.ticker:
            cache.clear_cache(ticker=args.ticker)
        else:
            confirm = input("Clear all cache? (yes/no): ")
            if confirm.lower() == 'yes':
                cache.clear_cache()


if __name__ == '__main__':
    main()
