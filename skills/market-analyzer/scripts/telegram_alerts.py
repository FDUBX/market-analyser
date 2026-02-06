#!/usr/bin/env python3
"""
Telegram Alert Wrapper for Live Monitor
Sends trading signals to Telegram
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from live_monitor import LiveMonitor
import json
from datetime import datetime

def format_buy_signal(signal, config):
    """Format a BUY signal for Telegram"""
    position_size = config['backtest']['position_size']
    stop_loss = config['backtest']['stop_loss']
    take_profit = config['backtest']['take_profit']
    
    capital = 10000  # Or get from portfolio
    position_value = capital * position_size
    shares = int(position_value / signal['price'])
    sl_price = signal['price'] * (1 - stop_loss)
    tp_price = signal['price'] * (1 + take_profit)
    
    msg = f"""🟢 **SIGNAL BUY**

📊 **{signal['ticker']}** @ ${signal['price']:.2f}
⭐ Score: {signal['score']:.1f}/10
💡 Raison: {signal['reason']}

💰 Position suggérée: {position_size*100:.0f}% (${position_value:,.0f})
📈 Shares: {shares}
🛑 Stop-loss: ${sl_price:.2f} (-{stop_loss*100:.0f}%)
🎯 Take-profit: ${tp_price:.2f} (+{take_profit*100:.0f}%)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    return msg

def format_sell_signal(signal):
    """Format a SELL signal for Telegram"""
    emoji = "🔴" if signal['pnl_pct'] < 0 else "🟢"
    
    msg = f"""{emoji} **SIGNAL SELL**

📊 **{signal['ticker']}** @ ${signal['price']:.2f}
⭐ Score: {signal['score']:.1f}/10
💡 Raison: {signal['reason']}

{'📉' if signal['pnl_pct'] < 0 else '📈'} P&L: {signal['pnl_pct']:+.2f}%
👥 Shares: {signal['shares']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    return msg

def format_portfolio_summary(state):
    """Format portfolio summary for Telegram"""
    initial = 10000
    pnl = state['total_value'] - initial
    pnl_pct = (pnl / initial) * 100
    
    msg = f"""💼 **Portfolio Status**

💰 Cash: ${state['cash']:,.2f}
📊 Total Value: ${state['total_value']:,.2f}
{'📈' if pnl >= 0 else '📉'} P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)

"""
    
    if state['positions']:
        msg += f"📍 **Positions ({len(state['positions'])}):**\n"
        for pos in state['positions']:
            pnl_emoji = "📈" if pos['pnl_pct'] >= 0 else "📉"
            msg += f"• {pos['ticker']}: {pos['shares']} @ ${pos['current_price'] or pos['avg_price']:.2f} {pnl_emoji} {pos['pnl_pct']:+.2f}%\n"
    else:
        msg += "📍 No open positions\n"
    
    msg += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    return msg

def send_telegram_message(message):
    """Send message via OpenClaw message tool"""
    # This will be called by OpenClaw via exec
    # The message is already formatted
    print("TELEGRAM_MESSAGE:")
    print(message)
    print("END_TELEGRAM_MESSAGE")

def main():
    monitor = LiveMonitor()
    
    # Load config
    with open('../config.json', 'r') as f:
        config = json.load(f)
    watchlist = config['watchlist']
    
    # Update prices and analyze
    monitor.update_positions_prices(watchlist)
    signals = monitor.analyze_market(watchlist)
    
    if signals:
        # Send individual signal alerts
        for signal in signals:
            if signal['action'] == 'BUY':
                msg = format_buy_signal(signal, config)
            else:
                msg = format_sell_signal(signal)
            
            send_telegram_message(msg)
        
        # Auto-execute if enabled
        if config.get('telegram', {}).get('auto_execute', False):
            for signal in signals:
                monitor.execute_signal(signal)
            
            monitor.calculate_total_value()
    
    # Send daily summary if configured
    now = datetime.now()
    summary_time = config.get('telegram', {}).get('daily_summary_time', '08:00')
    
    if now.strftime('%H:%M') == summary_time:
        state = monitor.get_portfolio_state()
        msg = format_portfolio_summary(state)
        send_telegram_message(msg)

if __name__ == '__main__':
    main()
