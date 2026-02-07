#!/bin/bash
# Cron wrapper that triggers agent notification via wake event

cd "$(dirname "$0")/.."

# Run analysis
OUTPUT=$(./live_trade analyze 2>&1)

# Log the output
echo "$(date '+%Y-%m-%d %H:%M:%S') - Live trading check" >> logs/live.log
echo "$OUTPUT" >> logs/live.log
echo "---" >> logs/live.log

# Check if signals were found
if echo "$OUTPUT" | grep -q "Signal(s) Found"; then
    # Extract signal count
    SIGNAL_COUNT=$(echo "$OUTPUT" | grep "Signal(s) Found" | grep -oP '\d+')
    
    # Create notification file for agent to process
    NOTIFY_DIR="notifications"
    mkdir -p "$NOTIFY_DIR"
    
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    NOTIFY_FILE="$NOTIFY_DIR/signal_${TIMESTAMP}.txt"
    
    cat > "$NOTIFY_FILE" << EOF
🚨 Market Analyzer Alert

${SIGNAL_COUNT} signal(s) détecté(s) !

$OUTPUT

⏰ $(date '+%Y-%m-%d %H:%M')
🔗 Dashboard: http://192.168.1.64:8080/live
EOF
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Notification file created: $NOTIFY_FILE" >> logs/live.log
    
    # The agent will pick this up via heartbeat and send to Telegram
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - No signals detected" >> logs/live.log
fi
