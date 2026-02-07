# Mode Simulation Auto - Activé ⚡

**Date d'activation :** 2026-02-07 10:04  
**Mode :** Exécution automatique des trades (paper trading virtuel)

---

## ✅ Configuration Actuelle

Le système est maintenant en **Mode Simulation Auto**.

### Ce qui se passe automatiquement :

**Tous les jours à 15h30 (lun-ven) :**
1. Analyse les 7 actions de la watchlist
2. Calcule les scores avec v2.1 (seuils 5.5/4.5)
3. Détecte les signaux BUY/SELL
4. **Exécute automatiquement** les trades sur le portfolio virtuel
5. Te notifie des trades effectués sur Telegram

### Types de Trades Automatiques

**🟢 BUY :**
- Score >= 5.5
- Pas de position ouverte sur ce ticker
- Cash disponible >= position_size (20%)
- Action : Achète automatiquement

**🔴 SELL :**
- Stop-loss atteint : Prix <= -5%
- Take-profit atteint : Prix >= +18%
- Score faible : Score <= 4.5
- Action : Vend automatiquement la position

---

## 📊 État Actuel du Portfolio

**Mise à jour :** 2026-02-07 10:04

| Métrique | Valeur |
|----------|--------|
| Capital Initial | $10,000.00 |
| Cash | $881.68 |
| Valeur Totale | $10,133.81 |
| **P&L** | **+$133.81 (+1.34%)** ✅ |

### Positions Ouvertes (5/7)

| Ticker | Shares | Prix Entrée | Prix Actuel | P&L | Valeur |
|--------|--------|-------------|-------------|-----|--------|
| AAPL | 7 | $275.91 | $278.12 | +0.80% | $1,946.84 |
| MSFT | 5 | $393.67 | $401.14 | +1.90% | $2,005.70 |
| GOOGL | 6 | $331.25 | $322.86 | -2.53% | $1,937.16 |
| NVDA | 11 | $171.88 | $185.41 | **+7.87%** 🚀 | $2,039.51 |
| META | 2 | $670.21 | $661.46 | -1.31% | $1,322.92 |

**Meilleure position :** NVDA +7.87% 🏆  
**À surveiller :** GOOGL -2.53% (proche du stop-loss à -5%)

---

## 🔔 Notifications Telegram

Tu recevras une notification **seulement si un trade est exécuté** :

### Exemple Notification BUY

```
⚡ Trade Automatique Exécuté

🟢 BUY 12 TSLA @ $245.50

Score: 5.8/10
Investissement: $2,946
Cash restant: $854

⏰ 2026-02-07 15:30
🔗 http://192.168.1.64:8080/live
```

### Exemple Notification SELL

```
⚡ Trade Automatique Exécuté

🔴 SELL 6 GOOGL @ $314.69 (STOP_LOSS)

P&L: -$99.36 (-5.00%) 📉
Capital récupéré: $1,888

⏰ 2026-02-07 15:30
🔗 http://192.168.1.64:8080/live
```

**Si aucun signal :** Pas de notification (silence = tout va bien)

---

## 📈 Suivi de Performance

### Dashboard Live

**URL :** http://192.168.1.64:8080/live

**Rafraîchissement :** Toutes les 5 minutes

**Affichage :**
- Portfolio en temps réel
- Positions ouvertes avec P&L
- Historique des trades
- Signaux détectés

### Logs

**Fichier :** `/home/pi/.openclaw/workspace/skills/market-analyzer/logs/live.log`

**Contenu :**
- Chaque exécution quotidienne
- Signaux détectés
- Trades exécutés
- Erreurs éventuelles

**Consulter :**
```bash
tail -50 logs/live.log
```

---

## ⚙️ Configuration Technique

**Script exécuté :** `scripts/cron_with_notify.sh`  
**Commande :** `./live_trade trade`  
**Base de données :** `scripts/live_portfolio.db`

**Cron job :**
```cron
30 15 * * 1-5 cd /home/pi/.openclaw/workspace/skills/market-analyzer && bash scripts/cron_with_notify.sh
```

---

## 🎯 Objectifs & Limites

### Objectifs du Mode Auto

1. **Validation stratégie** : Comparer backtest vs live
2. **Mesure discipline** : Aurais-tu vraiment suivi tous les signaux ?
3. **Test robustesse** : Performance en conditions réelles
4. **Benchmark** : Référence pour futures optimisations

### Limites à Comprendre

**❌ Ce n'est PAS :**
- De l'argent réel (virtuel uniquement)
- Une garantie de performance future
- Un système infaillible

**✅ Ce que c'est :**
- Un test en conditions réelles
- Un outil d'apprentissage
- Une validation de stratégie

---

## 📅 Calendrier d'Exécution

**Prochaines dates :**
- Lundi 10 février : 15h30
- Mardi 11 février : 15h30
- Mercredi 12 février : 15h30
- Jeudi 13 février : 15h30
- Vendredi 14 février : 15h30

**Pas d'exécution :**
- Weekends (samedi/dimanche)
- Jours fériés US (NYSE fermée)

---

## 🔄 Retour au Mode Alertes

Si tu veux revenir en mode "Alertes seulement" (pas d'exécution auto) :

**Option 1 : Via Script**
```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer/scripts
sed -i 's|./live_trade trade|./live_trade analyze|g' cron_with_notify.sh
```

**Option 2 : Demander à Molty**
> "Désactive le mode auto, je veux juste les alertes"

---

## 📊 Métriques à Surveiller

### Après 1 Mois

- **Return total** : Objectif > +5%
- **Win rate** : Objectif > 50%
- **Avg trade** : Profit moyen par trade
- **Max drawdown** : Perte maximale

### Après 3 Mois

- **Comparaison backtest** : Live vs backtests historiques
- **Sharpe ratio** : Rendement ajusté au risque
- **Volatilité** : Stabilité des returns

---

## ⚠️ Cas d'Arrêt Recommandés

**Stopper le mode auto si :**
- Drawdown > -15% (perte de $1,500)
- Performance < -10% pendant 2 mois consécutifs
- Comportement erratique (trop de stop-loss)

**Action :** Revenir en mode alertes, analyser, ajuster stratégie.

---

## 🧪 Test Immédiat Effectué

**Date :** 2026-02-07 10:05  
**Résultat :** ✅ Aucun signal détecté  
**Raison :** Toutes les positions dans leurs objectifs

**Interprétation :**
- Portfolio stable (5 positions)
- Aucun stop-loss/take-profit déclenché
- Scores actuels entre 4.5 et 5.5 (zone neutre)
- **Normal** : Le marché ne génère pas toujours des signaux

---

## 📝 Changelog

**2026-02-07 10:04** - Activation Mode Simulation Auto
- Modifié `cron_with_notify.sh` : `analyze` → `trade`
- Portfolio initial : $10,133.81 (+1.34%)
- 5 positions ouvertes

---

✅ **Le Mode Simulation Auto est maintenant actif et testé !**

**Prochaine exécution automatique :** Lundi 10 février à 15h30

🦎 **Le système trade maintenant seul. Détends-toi et observe !**
