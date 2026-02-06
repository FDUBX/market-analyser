#!/bin/bash
# Setup cron jobs for live trading automation

SKILL_DIR="/home/pi/.openclaw/workspace/skills/market-analyzer"

echo "🔧 Setting up cron jobs for Market Analyzer..."
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$SKILL_DIR/logs"

# Prepare cron entries
CRON_ENTRIES="
# Market Analyzer - Live Trading Automation
# Analyse quotidienne à l'ouverture NYSE (15:30 GMT+1)
30 15 * * 1-5 cd $SKILL_DIR && ./live_trade analyze >> logs/live.log 2>&1

# Résumé en fin de journée (22:00 GMT+1 - après clôture NYSE)
0 22 * * 1-5 cd $SKILL_DIR && ./live_trade status >> logs/live.log 2>&1
"

# Display cron entries
echo "Les entrées suivantes seront ajoutées à votre crontab :"
echo "$CRON_ENTRIES"
echo ""

# Ask for confirmation
read -p "Ajouter ces entrées à crontab ? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Annulé"
    exit 1
fi

# Backup existing crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Add new entries
(crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -

echo "✅ Cron jobs configurés !"
echo ""
echo "📅 Horaires :"
echo "  - 15:30 (lun-ven) : Analyse automatique à l'ouverture NYSE"
echo "  - 22:00 (lun-ven) : Résumé de fin de journée"
echo ""
echo "📝 Logs : $SKILL_DIR/logs/live.log"
echo ""
echo "Pour voir les cron jobs actifs :"
echo "  crontab -l"
echo ""
echo "Pour les supprimer :"
echo "  crontab -e  # puis supprimer les lignes Market Analyzer"
