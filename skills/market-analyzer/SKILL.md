# Market Analyzer Skill

**Version:** 2.1  
**Dernière mise à jour:** 2026-02-07

---

## Vue d'Ensemble

Système complet d'analyse de marché avec :
- **Backtesting** : Test de stratégies sur données historiques
- **Paper Trading** : Simulation en temps réel
- **Dashboard Web** : Interface de gestion
- **Alertes Telegram** : Notifications automatiques

---

## Commandes Principales

### 1. Analyse de Marché

```bash
cd $SKILL_DIR
python3 scripts/analyzer.py AAPL
```

Analyse un ticker et retourne :
- Score technique (RSI, MACD, Bollinger, Volume, SMA, ADX, Williams %R, OBV)
- Score fondamental (P/E, croissance, marges)
- Score sentiment (volume, momentum)
- Signal BUY/SELL/HOLD

### 2. Backtesting

```bash
python3 scripts/backtest.py --ticker AAPL --period 2y
```

Teste la stratégie sur historique :
- Performance (%)
- Nombre de trades
- Win rate
- Drawdown maximum

### 3. Paper Trading Live

```bash
./live_trade status    # Portfolio actuel
./live_trade analyze   # Signaux du jour
./live_trade trade     # Exécuter les trades (paper)
```

### 4. Dashboard

```bash
python3 scripts/dashboard_advanced.py
```

Interface web sur http://192.168.1.64:8080

---

## Configuration

**Fichier:** `config.json`

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
  }
}
```

**Version actuelle (v2.1) :**
- BUY threshold: 5.5
- SELL threshold: 4.5
- Performance validée: +33.27% moyenne sur 3 ans

---

## Intégration OpenClaw

### Analyse via Chat

**User:** "Analyse AAPL"

**Agent:**
```javascript
exec(`cd /home/pi/.openclaw/workspace/skills/market-analyzer && python3 scripts/analyzer.py AAPL`)
```

### Alerts Telegram

**User:** "Envoie-moi les signaux du jour"

**Agent:**
```javascript
// 1. Analyser le marché
const signals = exec(`cd /home/pi/.openclaw/workspace/skills/market-analyzer && ./live_trade analyze`)

// 2. Envoyer via message tool si signaux détectés
if (signals.includes('Signal(s) Found')) {
  message.send({
    channel: 'telegram',
    target: '6812190723',
    message: signals
  })
}
```

### Cron Job pour Monitoring Quotidien

**HEARTBEAT.md** pourrait inclure :

```markdown
## Market Check (once per day, weekdays only)

- Check if today is Mon-Fri
- If between 15:30-16:00 (NYSE opening in GMT+1):
  - Run: `/home/pi/.openclaw/workspace/skills/market-analyzer/live_trade analyze`
  - If signals found, notify via Telegram
```

---

## Structure des Fichiers

```
market-analyzer/
├── config.json              # Configuration principale
├── strategies.json          # Stratégies prédéfinies
├── SKILL.md                 # Ce fichier
├── LIVE_TRADING.md         # Guide du paper trading
├── OPTIMIZATION_RESULTS.md # Résultats backtests
├── live_trade              # Commande CLI principale
├── scripts/
│   ├── analyzer.py         # Moteur d'analyse (v2.1)
│   ├── portfolio_sim.py    # Simulateur de portfolio
│   ├── data_cache.py       # Cache SQLite
│   ├── live_monitor.py     # Paper trading live
│   ├── telegram_alerts.py  # Formattage Telegram
│   ├── dashboard_advanced.py # Interface web
│   └── ...
└── logs/
    └── live.log            # Logs du live trading
```

---

## Base de Données

### `data_cache.db`
- **prices** : Cours historiques (OHLCV)
- **info** : Métadonnées des tickers
- **Performance :** Cache ~3500 jours de données

### `portfolio_sim.db`
- **portfolios** : Backtests sauvegardés
- **positions** : Positions ouvertes
- **trades_log** : Historique complet

### `live_portfolio.db`
- **portfolio** : État du paper trading
- **positions** : Positions live actuelles
- **trades** : Historique live
- **signals** : Log des signaux

---

## API OpenClaw

### Analyser un Ticker

```javascript
const result = await exec({
  command: 'python3 scripts/analyzer.py AAPL',
  workdir: '/home/pi/.openclaw/workspace/skills/market-analyzer'
})

// Parse JSON output
const analysis = JSON.parse(result.stdout)
console.log(`Score: ${analysis.scores.total}`)
console.log(`Signal: ${analysis.signal}`)
```

### Envoyer Alerte Formatée

```javascript
const signal = {
  ticker: 'NVDA',
  action: 'BUY',
  score: 6.2,
  price: 171.88
}

const message = `🟢 SIGNAL ${signal.action}

📊 ${signal.ticker} @ $${signal.price}
⭐ Score: ${signal.score}/10`

await message_send({
  channel: 'telegram',
  target: '6812190723',
  message: message
})
```

---

## Performance

**v2.1 Validated (2023-2025) :**
- 2023: +52.29% (72 trades)
- 2024: +33.57% (68 trades)
- 2025: +13.93% (88 trades)
- **Moyenne : +33.27%/an**

**Comparé à v2.0 :**
- +0.65% de performance
- -39% de trades (moins de bruit)

---

## Exemples d'Usage

### 1. Check Quotidien Automatisé

Ajouter à `HEARTBEAT.md` :

```markdown
## Daily Market Check (weekdays 15:30 GMT+1)

- Run market analyzer
- If BUY/SELL signals → notify on Telegram
- Update paper trading portfolio
```

### 2. Alerte Manuelle

**User:** "Analyse le marché maintenant"

**Agent exécute:**
```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
./live_trade analyze
```

**Si signaux détectés**, envoie via Telegram.

### 3. Review Hebdomadaire

**User:** "Comment va mon portfolio paper trading ?"

**Agent exécute:**
```bash
./live_trade status
```

**Puis formate** la réponse de manière lisible.

---

## Dépendances

**Python packages** (voir `requirements.txt`) :
- yfinance
- pandas
- numpy
- fastapi + uvicorn (dashboard)
- python-telegram-bot (alertes)

**Installation :**
```bash
cd scripts
bash install_deps.sh
```

---

## Troubleshooting

### Rate Limits Yahoo Finance

**Solution :** Le cache (`data_cache.db`) évite 99% des appels API.  
Si besoin, pré-télécharger :

```bash
python3 scripts/data_cache.py --preload --tickers AAPL,MSFT,GOOGL --days 500
```

### Database Locked

**Cause :** Deux process simultanés  
**Solution :** Tuer les process ou attendre fin de l'autre

### "No data for ticker"

**Cause :** Marché fermé ou ticker invalide  
**Solution :** Vérifier watchlist, attendre ouverture NYSE

---

## Notes de Version

### v2.1 (2026-02-07)
- ✅ Optimisation seuils : 5.5/4.5
- ✅ Paper trading live
- ✅ Alertes Telegram (en cours)
- ✅ Performance: +33.27% validée sur 3 ans

### v2.0 (2026-02-06)
- ✅ 8 indicateurs techniques (vs 5 en v1.0)
- ✅ Data cache SQLite
- ✅ Optimisation grid search
- ✅ Dashboard avancé

### v1.0 (2026-02-02)
- ✅ Analyse technique de base
- ✅ Backtesting simple
- ✅ Dashboard basique

---

🦎 **Pour plus de détails :** Voir `LIVE_TRADING.md`, `OPTIMIZATION_RESULTS.md`, et `README.md`
