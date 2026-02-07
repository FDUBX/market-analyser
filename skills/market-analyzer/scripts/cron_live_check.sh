#!/bin/bash
# Cron wrapper for live trading checks with Telegram notifications
# This script is called by cron and sends notifications via OpenClaw message tool

cd "$(dirname "$0")/.."

# Gateway configuration
GATEWAY_URL="http://localhost:18789"
GATEWAY_TOKEN="d2a8e12b4171c491739729caaa55a94da04e19598b56686a"
TELEGRAM_USER="6812190723"

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
    
    # Format message for Telegram (clean format, no markdown issues)
    MESSAGE="🚨 Market Analyzer Alert

${SIGNAL_COUNT} signal(s) détecté(s) !

$OUTPUT

⏰ $(date '+%Y-%m-%d %H:%M')
🔗 Dashboard: http://192.168.1.64:8080/live
"
    
    # Create JSON payload (escape properly)
    PAYLOAD=$(cat <<EOF
{
  "action": "send",
  "channel": "telegram",
  "target": "$TELEGRAM_USER",
  "message": $(echo "$MESSAGE" | jq -Rs .)
}
EOF
)
    
    # Send via OpenClaw HTTP API
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/message" \
        -H "Authorization: Bearer $GATEWAY_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Telegram notification sent successfully" >> logs/live.log
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to send Telegram notification (HTTP $HTTP_CODE)" >> logs/live.log
        echo "$RESPONSE" >> logs/live.log
    fi
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - No signals detected" >> logs/live.log
fi
