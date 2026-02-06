# 2026-02-07 - Live Trading System Setup

## Time: 00:36-00:50 GMT+1

---

## Objectif

François a demandé un système pratique pour suivre les stratégies testées en mode réel.

**Choix:** A + C = Paper Trading + Alertes Telegram + Dashboard Live

---

## Ce qui a été créé

### 1. **Système de Paper Trading** ✅

**Fichier:** `scripts/live_monitor.py`

**Fonctionnalités:**
- Portfolio virtuel avec $10,000 initial
- Analyse quotidienne du marché
- Génération de signaux BUY/SELL
- Exécution automatique (simulation)
- Calcul P&L en temps réel
- Base de données SQLite (`live_portfolio.db`)

**Tables DB:**
- `portfolio` : État du portfolio (cash, valeur totale)
- `positions` : Positions ouvertes actuelles
- `trades` : Historique complet
- `signals` : Log de tous les signaux

### 2. **Alertes Telegram** ✅

**Fichier:** `scripts/telegram_alerts.py`

**Format des messages:**
- Signal BUY avec prix, score, stop-loss, take-profit
- Signal SELL avec P&L, raison (stop-loss, take-profit, low score)
- Résumé quotidien du portfolio

**Intégration OpenClaw:** Via message tool (à finaliser)

### 3. **Commande CLI Simple** ✅

**Fichier:** `live_trade` (root du skill)

**Usage:**
```bash
./live_trade status    # Voir portfolio
./live_trade analyze   # Analyser sans exécuter
./live_trade trade     # Analyser + exécuter
./live_trade alert     # Générer alertes Telegram
./live_trade reset     # Reset à $10,000
```

### 4. **Documentation Complète** ✅

**Fichiers:**
- `LIVE_TRADING.md` : Guide complet (8.6 KB)
- `SKILL.md` : Doc technique pour OpenClaw
- Exemples cron, troubleshooting, API usage

---

## Test Initial

**Commande:** `./live_trade analyze --execute`

**Résultat:**
- 5 signaux BUY détectés (AAPL, MSFT, GOOGL, NVDA, META)
- Tous les tickers au-dessus du seuil 5.5
- Exécution réussie : 5 positions ouvertes
- Capital investi : $9,118 / $10,000 (91%)
- Cash restant : $882

**Portfolio après premier trade:**
```
Ticker   Shares   Entry      Current    P&L %      Value       
------------------------------------------------------------
AAPL     7        $275.91    $275.91       +0.00% $   1931.37
MSFT     5        $393.67    $393.67       +0.00% $   1968.35
GOOGL    6        $331.25    $331.25       +0.00% $   1987.50
NVDA     11       $171.88    $171.88       +0.00% $   1890.68
META     2        $670.21    $670.21       +0.00% $   1340.42
```

---

## Prochaines Étapes

### Court Terme (À faire)

1. **Intégration Telegram complète**
   - Connecter `telegram_alerts.py` au message tool d'OpenClaw
   - Tester envoi de notifications réelles
   - Ajouter inline buttons (BUY confirmé, ignorer, etc.)

2. **Cron Job Setup**
   ```cron
   # Analyse quotidienne à 15h30 (ouverture NYSE en GMT+1)
   30 15 * * 1-5 cd /path/to/market-analyzer && ./live_trade analyze
   ```

3. **Dashboard Live (onglet)**
   - Ajouter onglet "Live" au dashboard actuel
   - Afficher positions en temps réel
   - Graphique de performance du paper trading
   - Liste des signaux récents

4. **Heartbeat Integration**
   - Ajouter check quotidien dans HEARTBEAT.md
   - Notifier François si signaux importants

### Moyen Terme

- [ ] Metrics de performance (Sharpe ratio, max drawdown)
- [ ] Trade journal avec notes
- [ ] Backtesting comparatif (paper vs stratégie)
- [ ] Multi-stratégies parallèles

---

## Configuration Recommandée

### `config.json` - Section Telegram

```json
"telegram": {
  "enabled": true,
  "auto_execute": false,        // Alertes seulement, pas d'exécution auto
  "daily_summary_time": "08:00", // Résumé du matin
  "alert_threshold": 6.0         // Score minimum pour alerte urgente
}
```

**Recommandation initiale:** `auto_execute: false`  
→ François reçoit les alertes et décide manuellement

**Après validation (1-3 mois):** Possibilité de passer à `true`

---

## Usage Quotidien Recommandé

### Routine Manuelle

```bash
# Matin (avant ouverture)
./live_trade status

# À l'ouverture NYSE (15h30 GMT+1)
./live_trade analyze

# Si signaux intéressants
./live_trade trade

# Fin de journée
./live_trade status
```

### Routine Automatisée (via cron)

```bash
# Le système analyse automatiquement
# Envoie alertes Telegram si signaux
# François review et décide
```

---

## Avantages du Système

✅ **Aucun risque financier** (paper money)  
✅ **Validation en conditions réelles** (prix live, volatilité réelle)  
✅ **Historique complet** (compare backtest vs live)  
✅ **Contrôle total** (François décide, système suggère)  
✅ **Notifications proactives** (pas besoin de checker manuellement)

---

## Différence Paper vs Real

| Aspect | Paper Trading | Real Trading |
|--------|---------------|--------------|
| Argent | Virtuel ($10k) | Réel |
| Risque | Zéro | Élevé |
| Exécution | Instantanée | Délais broker |
| Frais | Ignorés | Commission + spread |
| Slippage | Non | Oui (prix d'exécution ≠ prix demandé) |
| Émotions | Faibles | Fortes (peur, avidité) |

**Recommandation:** Valider 3+ mois en paper avant de considérer le real

---

## Fichiers Créés

- `scripts/live_monitor.py` (16 KB) - Moteur principal
- `scripts/telegram_alerts.py` (4 KB) - Formattage messages
- `scripts/run_live_monitor.sh` (1.3 KB) - Wrapper shell
- `live_trade` (1.7 KB) - Commande CLI
- `LIVE_TRADING.md` (8.6 KB) - Documentation
- `SKILL.md` (6.6 KB) - Doc technique
- `scripts/live_portfolio.db` (créée au runtime)

**Total:** ~38 KB de code + documentation

---

## Notes Techniques

**Database:** SQLite (portable, pas de serveur)  
**Update frequency:** À la demande ou via cron  
**Prix source:** Yahoo Finance via cache (évite rate limits)  
**Timezone:** Configurable, actuellement GMT+1 (Europe/Paris)

---

## Statut

✅ **Paper Trading:** Opérationnel  
🚧 **Telegram Alerts:** Formattage OK, envoi à finaliser  
⏳ **Dashboard Live:** À créer  
⏳ **Cron Job:** À configurer par François

---

**Session par:** Molty 🦎  
**Durée:** ~15 minutes  
**Prochaine étape:** Intégration Telegram + Dashboard Live

---

💡 **Note pour François:**

Le système est prêt à être testé ! Tu peux démarrer avec :

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
./live_trade analyze
```

Si les signaux te semblent bons :

```bash
./live_trade trade
```

Et pour voir l'évolution :

```bash
./live_trade status
```

C'est 100% virtuel, donc n'hésite pas à expérimenter ! 🚀
