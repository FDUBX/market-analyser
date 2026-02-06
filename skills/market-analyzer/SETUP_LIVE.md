# Setup Live Trading - Guide Complet 🚀

Ce guide explique comment configurer le système de Live Trading avec alertes Telegram et automation.

---

## ✅ Ce qui est déjà fait

1. **Paper Trading Engine** : `scripts/live_monitor.py`
2. **Dashboard Live** : Onglet "🔴 Live Trading" ajouté
3. **Scripts d'automation** : Cron wrappers prêts
4. **CLI** : Commande `./live_trade` opérationnelle

---

## 🚀 Configuration Rapide (5 minutes)

### Étape 1 : Lancer le Dashboard

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer/scripts
python3 dashboard_advanced.py
```

**Dashboard accessible sur :**
- http://192.168.1.64:8080
- Nouvel onglet : **🔴 Live Trading**

### Étape 2 : Initialiser le Portfolio

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
./live_trade analyze --execute
```

Cela va :
- Analyser les 7 actions de la watchlist
- Exécuter les signaux BUY/SELL
- Créer la base de données `scripts/live_portfolio.db`

### Étape 3 : Configurer le Cron (Automation)

```bash
cd scripts
bash setup_cron.sh
```

**Cela configurera :**
- Analyse quotidienne à 15h30 (ouverture NYSE en GMT+1)
- Résumé quotidien à 22h00 (après clôture)
- Logs dans `logs/live.log`

**Confirmation :**
```bash
crontab -l | grep "Market Analyzer"
```

---

## 📊 Dashboard Live - Fonctionnalités

### Vue d'ensemble

**Accès :** http://192.168.1.64:8080/live

**Affiche :**
1. **Portfolio Status**
   - Cash disponible
   - Valeur totale
   - P&L en $ et %
   - Auto-refresh toutes les 5 minutes

2. **Positions Ouvertes**
   - Ticker, shares, prix d'entrée/actuel
   - P&L par position
   - Stop-loss et Take-profit

3. **Signaux Actuels**
   - BUY/SELL détectés en temps réel
   - Score, prix, raison
   - Bouton "Exécuter" pour appliquer

4. **Historique**
   - 10 derniers trades
   - Date, action, P&L

### Actions Disponibles

- **⚡ Exécuter les Signaux** : Applique tous les signaux BUY/SELL
- **🔄 Rafraîchir** : Recharge les prix actuels
- **🔄 Reset Portfolio** : Remet à $10,000 (⚠️ Efface tout)

---

## 🔔 Alertes Telegram

### Configuration Actuelle

Les alertes Telegram sont configurées pour être envoyées via l'API OpenClaw.

**Fichier :** `scripts/cron_live_check.sh`

**Fonctionnement :**
1. Cron exécute le script à 15h30 (lun-ven)
2. Le script analyse le marché
3. Si signaux détectés → envoi notification Telegram
4. Message inclut : nombre de signaux, détails, lien dashboard

### Format du Message

```
🚨 Market Analyzer Alert

3 signal(s) détecté(s) !

🟢 BUY NVDA
   Score: 6.2/10
   Price: $171.88
   Reason: HIGH_SCORE

🔴 SELL AAPL
   Score: 4.2/10
   Price: $275.91
   P&L: -2.5%
   Reason: STOP_LOSS

...

⏰ 2026-02-07 15:30
🔗 Dashboard: http://192.168.1.64:8080/live
```

### Test Manuel

Pour tester l'envoi d'une alerte :

```bash
cd scripts
bash cron_live_check.sh
```

Vérifier les logs :
```bash
tail -f logs/live.log
```

---

## ⏰ Horaires Recommandés (Europe/Paris GMT+1)

### Marché US (NYSE)

- **Ouverture :** 15:30 GMT+1 (9:30 AM ET)
- **Clôture :** 22:00 GMT+1 (4:00 PM ET)

### Cron Jobs Configurés

```cron
# Analyse à l'ouverture (15:30)
30 15 * * 1-5 cd /path/to/market-analyzer && ./live_trade analyze

# Résumé après clôture (22:00)
0 22 * * 1-5 cd /path/to/market-analyzer && ./live_trade status
```

### Personnalisation

Pour ajuster les horaires :

```bash
crontab -e
```

Modifier les heures selon tes préférences.

---

## 🎯 Configuration Avancée

### Auto-exécution des Trades

**Par défaut :** Alertes seulement, pas d'exécution automatique

**Pour activer l'auto-exécution :**

Éditer `config.json` :

```json
{
  "telegram": {
    "enabled": true,
    "auto_execute": true,    // ⚠️ Change false → true
    "daily_summary_time": "08:00"
  }
}
```

Puis modifier le cron job :

```bash
crontab -e
```

Remplacer :
```cron
30 15 * * 1-5 cd /path && ./live_trade analyze
```

Par :
```cron
30 15 * * 1-5 cd /path && ./live_trade trade    # Execute au lieu d'analyze
```

**⚠️ Attention :**
- L'auto-exécution applique tous les signaux automatiquement
- Recommandé seulement après validation de 1-3 mois
- Reste du paper trading (pas de vrai argent)

### Seuils d'Alerte Personnalisés

Éditer `config.json` :

```json
{
  "telegram": {
    "alert_threshold": 6.0    // Alerte seulement si score >= 6.0
  }
}
```

Par défaut, toutes les alertes sont envoyées. Avec un seuil, seules les alertes importantes sont notifiées.

### Watchlist Personnalisée

Éditer `config.json` :

```json
{
  "watchlist": [
    "AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMZN", "META",
    "AMD", "INTC", "NFLX"    // Ajouter d'autres tickers
  ]
}
```

---

## 🛠️ Maintenance

### Vérifier le Statut

```bash
./live_trade status
```

### Voir les Logs

```bash
tail -f logs/live.log
```

### Nettoyer les Logs

```bash
> logs/live.log    # Vide le fichier
```

### Backup de la Base de Données

```bash
cp scripts/live_portfolio.db scripts/live_portfolio_backup_$(date +%Y%m%d).db
```

### Restaurer un Backup

```bash
cp scripts/live_portfolio_backup_20260207.db scripts/live_portfolio.db
```

---

## 📈 Monitoring de Performance

### Commandes Utiles

```bash
# Voir le portfolio
./live_trade status

# Analyser sans exécuter
./live_trade analyze

# Historique des trades (SQLite)
cd scripts
python3 -c "
import sqlite3
conn = sqlite3.connect('live_portfolio.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT 20')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

### Métriques Clés à Surveiller

- **Return %** : Performance globale
- **Win Rate** : % de trades gagnants
- **Avg Trade** : Profit moyen par trade
- **Max Drawdown** : Perte maximale subie

---

## 🐛 Troubleshooting

### "Database is locked"

**Cause :** Deux processus accèdent à la DB simultanément

**Solution :**
```bash
# Tuer les processus python
pkill -f live_monitor

# Attendre 5 secondes
sleep 5

# Relancer
./live_trade status
```

### "No data for ticker"

**Cause :** Marché fermé ou données manquantes

**Solution :**
```bash
# Pré-charger le cache
cd scripts
python3 -c "
from data_cache import DataCache
cache = DataCache()
cache.preload_tickers(['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMZN', 'META'], days=200)
"
```

### Dashboard ne démarre pas

**Cause :** Port déjà utilisé ou dépendances manquantes

**Solution :**
```bash
# Vérifier les dépendances
pip3 install -r requirements.txt

# Changer de port
python3 scripts/dashboard_advanced.py --port 8081
```

### Telegram ne reçoit pas d'alertes

**Cause :** OpenClaw API non accessible ou token invalide

**Solution :**
```bash
# Tester l'API OpenClaw
curl -X GET "http://localhost:18789/api/v1/status" \
  -H "Authorization: Bearer d2a8e12b4171c491739729caaa55a94da04e19598b56686a"

# Si échec, vérifier que OpenClaw tourne
openclaw status
```

---

## 📚 Ressources

**Documentation :**
- `LIVE_TRADING.md` : Guide d'utilisation détaillé
- `SKILL.md` : Documentation technique
- `OPTIMIZATION_RESULTS.md` : Résultats backtests

**Commandes :**
- `./live_trade --help` : Aide CLI
- Dashboard : http://192.168.1.64:8080/live

**Logs :**
- `logs/live.log` : Logs du monitoring
- `scripts/live_portfolio.db` : Base de données

---

## ✅ Checklist de Mise en Service

- [ ] Dashboard lancé et accessible
- [ ] Portfolio initialisé (première analyse)
- [ ] Cron jobs configurés
- [ ] Test d'alerte Telegram réussi
- [ ] Logs vérifiés

**Commandes pour tout vérifier :**

```bash
# 1. Dashboard
curl -s http://192.168.1.64:8080/live | grep "Portfolio Status"

# 2. Portfolio
./live_trade status | grep "Total Value"

# 3. Cron
crontab -l | grep "Market Analyzer"

# 4. Logs
tail -1 logs/live.log
```

---

🦎 **Système prêt ! Bon trading !**

**Prochaine étape :** Laisser tourner 1-2 semaines pour validation, puis ajuster la stratégie si nécessaire.
