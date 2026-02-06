#!/bin/bash
# Cron wrapper for live trading checks with Telegram notifications
# This script is called by cron and sends notifications via OpenClaw

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
    
    # Format message for Telegram
    MESSAGE="🚨 **Market Analyzer Alert**

$SIGNAL_COUNT signal(s) détecté(s) !

\`\`\`
$OUTPUT
\`\`\`

⏰ $(date '+%Y-%m-%d %H:%M')

🔗 Dashboard: http://192.168.1.64:8080/live
"
    
    # Send via OpenClaw (assuming openclaw CLI is available)
    # Alternative: Use HTTP API directly
    curl -s -X POST "http://localhost:18789/api/v1/message/send" \
        -H "Authorization: Bearer d2a8e12b4171c491739729caaa55a94da04e19598b56686a" \
        -H "Content-Type: application/json" \
        -d "{
            \"channel\": \"telegram\",
            \"target\": \"6812190723\",
            \"message\": $(echo "$MESSAGE" | jq -Rs .)
        }" > /dev/null 2>&1
    
    # If curl fails, log it
    if [ $? -ne 0 ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to send Telegram notification" >> logs/live.log
    fi
fi
