#!/bin/bash
# Install Market Analyzer Dashboard as systemd service

echo "🔧 Installation du service systemd Market Analyzer Dashboard"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Ce script doit être exécuté avec sudo"
    echo "Usage: sudo bash install_service.sh"
    exit 1
fi

SKILL_DIR="/home/pi/.openclaw/workspace/skills/market-analyzer"

# Create logs directory
mkdir -p "$SKILL_DIR/logs"
chown pi:pi "$SKILL_DIR/logs"

# Stop existing dashboard process
echo "🛑 Arrêt du dashboard existant..."
pkill -f dashboard_advanced.py || true
sleep 2

# Create service file
echo "📝 Création du fichier service..."
cat > /etc/systemd/system/market-analyzer-dashboard.service << 'EOF'
[Unit]
Description=Market Analyzer Dashboard
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/.openclaw/workspace/skills/market-analyzer/scripts
ExecStart=/usr/bin/python3 /home/pi/.openclaw/workspace/skills/market-analyzer/scripts/dashboard_advanced.py --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10
StandardOutput=append:/home/pi/.openclaw/workspace/skills/market-analyzer/logs/dashboard.log
StandardError=append:/home/pi/.openclaw/workspace/skills/market-analyzer/logs/dashboard.log

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Rechargement de systemd..."
systemctl daemon-reload

# Enable service (start at boot)
echo "✅ Activation du service au démarrage..."
systemctl enable market-analyzer-dashboard.service

# Start service
echo "🚀 Démarrage du service..."
systemctl start market-analyzer-dashboard.service

# Wait a bit and check status
sleep 3
echo ""
echo "📊 Statut du service :"
systemctl status market-analyzer-dashboard.service --no-pager -l

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Commandes utiles :"
echo "  sudo systemctl status market-analyzer-dashboard   # Voir le statut"
echo "  sudo systemctl stop market-analyzer-dashboard     # Arrêter"
echo "  sudo systemctl start market-analyzer-dashboard    # Démarrer"
echo "  sudo systemctl restart market-analyzer-dashboard  # Redémarrer"
echo "  sudo journalctl -u market-analyzer-dashboard -f   # Voir les logs en temps réel"
echo ""
echo "📍 Dashboard accessible sur : http://192.168.1.64:8080"
