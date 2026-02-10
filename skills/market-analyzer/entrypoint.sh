#!/bin/bash
set -e

DATA_DIR="/data"
APP_DIR="/app"

echo "🚀 Market Analyzer - Starting up..."

# Initialize data directory structure
mkdir -p "$DATA_DIR/notifications/sent"
mkdir -p "$DATA_DIR/logs"

# Bootstrap config.json if not present
if [ ! -f "$DATA_DIR/config.json" ]; then
    echo "📋 First run: copying default config..."
    cp "$APP_DIR/config.example.json" "$DATA_DIR/config.json"
fi

# Bootstrap strategies.json if not present
if [ ! -f "$DATA_DIR/strategies.json" ]; then
    echo "📋 First run: copying default strategies..."
    cp "$APP_DIR/strategies.json" "$DATA_DIR/strategies.json"
fi

# Create symlinks: point app files to /data
ln -sf "$DATA_DIR/config.json" "$APP_DIR/config.json"
ln -sf "$DATA_DIR/strategies.json" "$APP_DIR/strategies.json"
ln -sf "$DATA_DIR/notifications" "$APP_DIR/notifications"
ln -sf "$DATA_DIR/logs" "$APP_DIR/logs"

# Symlink databases from scripts dir to /data
ln -sf "$DATA_DIR/data_cache.db" "$APP_DIR/scripts/data_cache.db"
ln -sf "$DATA_DIR/portfolio_sim.db" "$APP_DIR/scripts/portfolio_sim.db"
ln -sf "$DATA_DIR/live_portfolio.db" "$APP_DIR/scripts/live_portfolio.db"

echo "✅ Data directory ready: $DATA_DIR"
echo "📍 Starting dashboard on port ${PORT:-8080}..."

exec python3 "$APP_DIR/scripts/dashboard_advanced.py" --host 0.0.0.0 --port "${PORT:-8080}"
