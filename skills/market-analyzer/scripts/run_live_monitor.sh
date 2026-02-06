#!/bin/bash
# Live Monitor with Telegram Alerts
# Run this via cron for automated monitoring

cd "$(dirname "$0")"

# Run monitor and capture output
OUTPUT=$(python3 telegram_alerts.py 2>&1)

# Check for Telegram messages to send
if echo "$OUTPUT" | grep -q "TELEGRAM_MESSAGE:"; then
    # Extract messages and send via OpenClaw
    echo "$OUTPUT" | awk '/TELEGRAM_MESSAGE:/,/END_TELEGRAM_MESSAGE/' | grep -v "TELEGRAM_MESSAGE:" | grep -v "END_TELEGRAM_MESSAGE" | while IFS= read -r line; do
        if [ ! -z "$line" ]; then
            MESSAGE="$MESSAGE$line\n"
        fi
        
        # Send when we hit a blank line or end
        if [ -z "$line" ] && [ ! -z "$MESSAGE" ]; then
            # Send via OpenClaw CLI (will use configured Telegram)
            # This assumes OpenClaw is running as a service
            curl -s -X POST "http://localhost:18789/api/message/send" \
                -H "Authorization: Bearer d2a8e12b4171c491739729caaa55a94da04e19598b56686a" \
                -H "Content-Type: application/json" \
                -d "{\"channel\": \"telegram\", \"target\": \"6812190723\", \"message\": \"$(echo -e $MESSAGE)\"}" \
                > /dev/null
            
            MESSAGE=""
        fi
    done
fi

# Log the run
echo "$(date): Live monitor ran" >> ../logs/monitor.log
