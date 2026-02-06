# Live Trading Guide 📈

Guide complet du système de Paper Trading avec alertes Telegram en temps réel.

---

## 🎯 Vue d'Ensemble

Le système de Live Trading permet de :
- **Paper Trading** : Simuler des trades en temps réel sans risque
- **Alertes Telegram** : Recevoir des notifications instantanées
- **Dashboard Live** : Visualiser les positions et performance
- **Automatisation** : Analyse quotidienne automatique via cron

---

## 🚀 Démarrage Rapide

### Commande Simple

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
./live_trade [command]
```

**Commandes disponibles :**

```bash
./live_trade status    # Voir le portfolio actuel
./live_trade analyze   # Analyser le marché (sans exécuter)
./live_trade trade     # Analyser + exécuter les trades
./live_trade alert     # Générer alertes Telegram
./live_trade reset     # Reset portfolio à $10,000
```

---

## 📊 Utilisation

### 1. Vérifier le Portfolio

```bash
./live_trade status
```

**Affiche :**
- Cash disponible
- Valeur totale du portfolio
- P&L (profit/perte) en $ et %
- Liste des positions ouvertes avec P&L par action

**Exemple de sortie :**
```
💼 Portfolio Status
============================================================
💰 Cash: $881.68
📊 Total Value: $10,000.00
📈 P&L: $+0.00 (+0.00%)
🕐 Last Updated: 2026-02-07T00:42:16

📍 Positions:
Ticker   Shares   Entry      Current    P&L %      Value       
------------------------------------------------------------
AAPL     7        $275.91    $275.91       +0.00% $   1931.37
MSFT     5        $393.67    $393.67       +0.00% $   1968.35
...
```

### 2. Analyser le Marché (Mode Lecture Seule)

```bash
./live_trade analyze
```

**Fonction :**
- Télécharge les derniers cours
- Analyse tous les tickers de la watchlist
- Génère des signaux BUY/SELL
- **N'exécute PAS** les trades (mode read-only)

**Utilise quand :**
- Tu veux juste voir les opportunités
- Vérifier avant d'exécuter manuellement
- Review de fin de journée

**Exemple de sortie :**
```
🔍 Analyzing 7 stocks...

🚨 2 Signal(s) Found:

🟢 BUY NVDA
   Score: 6.2/10
   Price: $171.88
   Reason: HIGH_SCORE

🔴 SELL AAPL
   Score: 4.3/10
   Price: $275.91
   P&L: -2.5%
   Reason: LOW_SCORE
```

### 3. Exécuter les Trades (Paper Trading)

```bash
./live_trade trade
```

**Fonction :**
- Analyse le marché
- **Exécute automatiquement** tous les signaux
- Met à jour le portfolio virtuel
- Affiche les résultats

**Utilise quand :**
- Tu fais confiance au système
- Mode automatique quotidien
- Backtesting en temps réel

### 4. Envoyer Alertes Telegram

```bash
./live_trade alert
```

**Fonction :**
- Génère les signaux
- Formate les messages pour Telegram
- **Note :** Actuellement affiche les messages, intégration OpenClaw en cours

**Format des alertes :**

**Signal BUY :**
```
🟢 SIGNAL BUY

📊 NVDA @ $171.88
⭐ Score: 6.2/10
💡 Raison: HIGH_SCORE

💰 Position suggérée: 20% ($2,000)
📈 Shares: 11
🛑 Stop-loss: $163.29 (-5%)
🎯 Take-profit: $202.82 (+18%)

⏰ 2026-02-07 09:30
```

**Signal SELL :**
```
🔴 SIGNAL SELL

📊 AAPL @ $275.91
⭐ Score: 4.3/10
💡 Raison: STOP_LOSS

📉 P&L: -5.12%
👥 Shares: 7

⏰ 2026-02-07 14:15
```

---

## ⚙️ Configuration

### Fichier : `config.json`

```json
{
  "watchlist": ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMZN", "META"],
  "thresholds": {
    "buy": 5.5,
    "sell": 4.5
  },
  "backtest": {
    "initial_capital": 10000,
    "position_size": 0.2,
    "stop_loss": 0.05,
    "take_profit": 0.18
  },
  "telegram": {
    "enabled": true,
    "auto_execute": false,
    "daily_summary_time": "08:00",
    "alert_threshold": 6.0
  }
}
```

**Paramètres clés :**

- `auto_execute: false` → Alertes uniquement, pas d'exécution auto
- `auto_execute: true` → Exécute les trades automatiquement
- `daily_summary_time` → Heure pour le résumé quotidien
- `alert_threshold` → Score minimum pour déclencher une alerte urgente

---

## 🤖 Automatisation via Cron

### Setup Quotidien (Analyse à 9h30 - Ouverture NYSE)

```bash
crontab -e
```

Ajouter :

```cron
# Market Analyzer - Analyse quotidienne
30 9 * * 1-5 cd /home/pi/.openclaw/workspace/skills/market-analyzer && ./live_trade analyze >> logs/live.log 2>&1

# Avec exécution automatique (si auto_execute: true)
30 9 * * 1-5 cd /home/pi/.openclaw/workspace/skills/market-analyzer && ./live_trade trade >> logs/live.log 2>&1

# Résumé en fin de journée (16h00 - Clôture NYSE)
0 16 * * 1-5 cd /home/pi/.openclaw/workspace/skills/market-analyzer && ./live_trade status >> logs/live.log 2>&1
```

**Fuseaux horaires :**
- NYSE ouvre à 9:30 AM ET
- Pour Europe/Paris (GMT+1) : NYSE ouvre à 15h30
- Ajuster les horaires selon ta timezone

---

## 📂 Base de Données

### Fichier : `scripts/live_portfolio.db`

**Tables :**

1. **portfolio** : État du portfolio (cash, valeur totale)
2. **positions** : Positions ouvertes actuelles
3. **trades** : Historique complet des trades
4. **signals** : Log de tous les signaux générés

### Consulter les Données

```bash
cd scripts
python3 -c "
import sqlite3
conn = sqlite3.connect('live_portfolio.db')
cursor = conn.cursor()

# Voir l'historique des trades
cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10')
for row in cursor.fetchall():
    print(row)

conn.close()
"
```

---

## 🎨 Dashboard Live (À venir)

Interface web pour :
- Visualiser positions en temps réel
- Graphiques de performance
- Historique des trades
- Configuration du système

**URL :** http://192.168.1.64:8080/live

---

## ⚠️ Important

### Paper Trading vs Real Trading

**Ce que fait le système :**
- ✅ Simule des trades avec prix réels
- ✅ Maintient un portfolio virtuel
- ✅ Calcule P&L réaliste
- ✅ **AUCUN ARGENT RÉEL**

**Ce que le système NE fait PAS :**
- ❌ Se connecter à un broker réel
- ❌ Exécuter des ordres réels
- ❌ Manipuler de l'argent réel

### Passage au Real Trading

**Avant de passer au réel :**
1. ✅ Valider stratégie sur 3+ mois en paper trading
2. ✅ Comparer performance paper vs backtest
3. ✅ Comprendre tous les signaux générés
4. ✅ Tester en période de volatilité
5. ✅ Avoir un plan de risk management

**Puis :**
- Démarrer avec un petit capital test
- Exécuter manuellement au début
- Ne jamais activer auto-execute sans surveillance

---

## 📊 Exemples d'Utilisation

### Routine Quotidienne Manuelle

```bash
# Matin (avant ouverture)
./live_trade status          # Voir positions overnight

# Ouverture (9:30 AM ET)
./live_trade analyze         # Checker les signaux

# Si signaux intéressants
./live_trade trade           # Exécuter (paper trading)

# Fin de journée
./live_trade status          # Review de la journée
```

### Routine Automatisée

```bash
# Setup une fois
crontab -e
# Ajouter les lignes cron ci-dessus

# Le système tourne seul
# Tu reçois les alertes Telegram
# Tu peux review via ./live_trade status
```

### Reset et Redémarrage

```bash
# Reset complet
./live_trade reset

# Réinitialise à $10,000
# Efface toutes les positions
# Garde l'historique des trades (dans archives)
```

---

## 🔧 Troubleshooting

### "No data for ticker X"

**Cause :** Ticker invalide ou marché fermé  
**Solution :** Vérifier la watchlist, attendre ouverture NYSE

### "Insufficient cash for trade"

**Cause :** Pas assez de cash pour nouvelles positions  
**Solution :** Ajuster `position_size` ou vendre des positions

### "No signals - all positions within targets"

**Cause :** Aucun signal BUY/SELL détecté  
**Solution :** Normal ! Le marché ne génère pas toujours des signaux

### Database locked

**Cause :** Deux instances tournent en même temps  
**Solution :** Tuer les process en cours, relancer

---

## 📈 Métriques de Performance

Le système track automatiquement :
- **Return total** : % de gain/perte depuis le début
- **Win rate** : % de trades gagnants
- **Average trade** : Profit moyen par trade
- **Sharpe ratio** : Rendement ajusté au risque (à venir)
- **Max drawdown** : Perte maximale subie (à venir)

---

## 🚀 Prochaines Fonctionnalités

- [ ] Dashboard web interactif
- [ ] Intégration Telegram complète (inline buttons)
- [ ] Backtesting comparatif (paper vs stratégie)
- [ ] Risk metrics (Sharpe, Sortino, max drawdown)
- [ ] Multi-stratégies (tester plusieurs configs en parallèle)
- [ ] Portfolio rebalancing automatique
- [ ] Trade journal avec notes manuelles

---

## 📝 Notes

**Capital initial :** $10,000 (modifiable dans config.json)  
**Position size :** 20% par trade (max 5 positions simultanées)  
**Stop-loss :** -5% (protection)  
**Take-profit :** +18% (objectif)  

**Watchlist :** 7 tech stocks (FAANG + NVDA + TSLA)

---

🦎 **Bon trading ! Remember: It's paper money, so experiment freely!**
