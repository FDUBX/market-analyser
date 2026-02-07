#!/bin/bash
# Start dashboard in persistent mode

SKILL_DIR="/home/pi/.openclaw/workspace/skills/market-analyzer"
cd "$SKILL_DIR/scripts"

# Kill existing dashboard if running
pkill -f dashboard_advanced.py

# Start dashboard with nohup (persistent)
nohup python3 dashboard_advanced.py --host 0.0.0.0 --port 8080 > ../logs/dashboard.log 2>&1 &

echo "✅ Dashboard started in background"
echo "📍 http://192.168.1.64:8080"
echo "📝 Logs: $SKILL_DIR/logs/dashboard.log"
echo ""
echo "To stop: pkill -f dashboard_advanced.py"
