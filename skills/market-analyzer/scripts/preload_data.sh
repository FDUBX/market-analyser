#!/bin/bash
# Preload data for common stocks

echo "📥 Préchargement des données historiques..."
echo ""

# Default universe
TICKERS="AAPL MSFT GOOGL NVDA TSLA AMZN META"

# Default date range (2 years)
START_DATE=$(date -d '2 years ago' '+%Y-%m-%d')
END_DATE=$(date '+%Y-%m-%d')

# Allow custom parameters
if [ "$1" ]; then
    START_DATE=$1
fi

if [ "$2" ]; then
    END_DATE=$2
fi

if [ "$3" ]; then
    TICKERS=$3
fi

echo "📅 Période: $START_DATE → $END_DATE"
echo "🎯 Actions: $TICKERS"
echo ""

cd "$(dirname "$0")"

python3 data_cache.py preload --tickers $TICKERS --start $START_DATE --end $END_DATE

echo ""
echo "✅ Préchargement terminé!"
echo ""
echo "📊 Statistiques du cache:"
python3 data_cache.py stats
