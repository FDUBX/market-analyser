#!/bin/bash
# Cron wrapper that triggers agent notification via wake event
# MODE: Simulation Auto (executes trades automatically)

cd "$(dirname "$0")/.."

# Run analysis + execution (Simulation Auto mode)
OUTPUT=$(./live_trade trade 2>&1)

# Log the output
echo "$(date '+%Y-%m-%d %H:%M:%S') - Live trading check" >> logs/live.log
echo "$OUTPUT" >> logs/live.log
echo "---" >> logs/live.log

# Create notification directory
NOTIFY_DIR="notifications"
mkdir -p "$NOTIFY_DIR"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
NOTIFY_FILE="$NOTIFY_DIR/daily_${TIMESTAMP}.txt"

# Check if signals were found
if echo "$OUTPUT" | grep -q "Signal(s) Found"; then
    # Extract signal count
    SIGNAL_COUNT=$(echo "$OUTPUT" | grep "Signal(s) Found" | grep -oP '\d+')
    
    # Create alert notification
    cat > "$NOTIFY_FILE" << EOF
🚨 Market Analyzer Alert

${SIGNAL_COUNT} signal(s) détecté(s) !

$OUTPUT

⏰ $(date '+%Y-%m-%d %H:%M')
🔗 Dashboard: http://192.168.1.64:8080/live
EOF
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Signal notification created: $NOTIFY_FILE" >> logs/live.log
else
    # No signals - create daily report
    PORTFOLIO_STATUS=$(./live_trade status 2>&1)
    
    cat > "$NOTIFY_FILE" << EOF
📊 Market Analyzer - Rapport Quotidien

✅ Aucun signal détecté aujourd'hui

$PORTFOLIO_STATUS

💡 Analyse effectuée : Toutes les positions sont dans leurs objectifs
⏰ $(date '+%Y-%m-%d %H:%M')
🔗 Dashboard: http://192.168.1.64:8080/live
EOF
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Daily report notification created: $NOTIFY_FILE" >> logs/live.log
fi
