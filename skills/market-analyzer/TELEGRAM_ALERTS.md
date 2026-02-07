# Alertes Telegram - Market Analyzer 📱

Guide complet du système d'alertes Telegram automatiques.

---

## ✅ Système Configuré

Les alertes Telegram sont maintenant **opérationnelles** et s'envoient automatiquement via le heartbeat de l'agent.

---

## 🔄 Comment Ça Marche

### 1. Cron Job (Analyse Quotidienne)

**Horaire :** 15h30 GMT+1 (lun-ven)

Le cron job exécute `scripts/cron_with_notify.sh` qui :
1. Analyse les 7 actions de la watchlist
2. Détecte les signaux BUY/SELL
3. **Si signaux détectés** → Crée un fichier dans `notifications/`
4. **Si aucun signal** → Log seulement

### 2. Agent Heartbeat (Envoi Notifications)

**Fréquence :** À chaque heartbeat (~30 min)

L'agent vérifie `notifications/` :
1. Lit les fichiers `.txt` non traités
2. Envoie le contenu sur Telegram
3. Déplace le fichier dans `notifications/sent/`

**Avantages :**
- ✅ Découplage cron/notification
- ✅ Pas de dépendance API externe
- ✅ Traçabilité complète (fichiers archivés)
- ✅ Réessai automatique si heartbeat échoue

---

## 📬 Format des Alertes

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

🟢 BUY GOOGL
   Score: 5.8/10
   Price: $331.25
   Reason: HIGH_SCORE

⏰ 2026-02-07 15:30
🔗 Dashboard: http://192.168.1.64:8080/live
```

---

## 🧪 Test des Alertes

### Test Immédiat

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
bash scripts/cron_with_notify.sh
```

Cela va :
1. Analyser le marché maintenant
2. Créer une notification si signaux
3. Le prochain heartbeat (~30 min) l'enverra

### Test Forcé (Sans Attendre)

Créer un fichier de notification manuellement :

```bash
cat > notifications/test.txt << 'EOF'
🧪 Test Manuel

Ceci est un test des alertes Telegram.

⏰ $(date '+%Y-%m-%d %H:%M')
EOF
```

Le prochain heartbeat l'enverra automatiquement.

---

## 📊 Monitoring

### Voir les Notifications En Attente

```bash
ls -l /home/pi/.openclaw/workspace/skills/market-analyzer/notifications/
```

### Voir les Notifications Envoyées

```bash
ls -l /home/pi/.openclaw/workspace/skills/market-analyzer/notifications/sent/
```

### Voir les Logs Cron

```bash
tail -50 /home/pi/.openclaw/workspace/skills/market-analyzer/logs/live.log
```

---

## ⚙️ Configuration

### Fichiers Clés

| Fichier | Rôle |
|---------|------|
| `crontab` | Déclenche analyse à 15h30 |
| `scripts/cron_with_notify.sh` | Analyse + crée notification |
| `notifications/` | Files d'attente messages |
| `HEARTBEAT.md` | Config agent pour envoi |

### Modifier l'Horaire

```bash
crontab -e
```

Modifier la ligne :
```cron
30 15 * * 1-5 ...   # Changer 30 15 pour autre horaire
```

Exemples :
- `00 14 * * 1-5` → 14h00 tous les jours ouvrés
- `30 9,15 * * 1-5` → 9h30 ET 15h30 tous les jours

### Changer la Fréquence Heartbeat

Par défaut : ~30 minutes

Pour changer, modifier la config OpenClaw (hors scope de ce doc).

---

## 🚨 Types de Signaux

### Signal BUY 🟢

Envoyé quand :
- Score >= 5.5 (seuil v2.1)
- Pas de position ouverte sur ce ticker
- Cash disponible suffisant

**Contenu :**
- Ticker
- Score/10
- Prix actuel
- Raison (HIGH_SCORE)

### Signal SELL 🔴

Envoyé quand :
- **Stop-loss atteint** : Prix <= -5%
- **Take-profit atteint** : Prix >= +18%
- **Score faible** : Score <= 4.5

**Contenu :**
- Ticker
- Score/10
- Prix actuel
- P&L actuel
- Raison (STOP_LOSS, TAKE_PROFIT, LOW_SCORE)

---

## 🔧 Troubleshooting

### Pas de notification reçue

**1. Vérifier qu'il y avait des signaux**

```bash
tail -20 logs/live.log
```

Si aucun signal détecté → Normal

**2. Vérifier les fichiers de notification**

```bash
ls notifications/
```

Si vide → Aucun signal créé  
Si fichiers présents → En attente du prochain heartbeat

**3. Forcer l'envoi immédiat**

Demander à Molty :
> "Vérifie les notifications Market Analyzer"

### Notifications en double

**Cause :** Fichier non déplacé dans `sent/`

**Solution :**
```bash
# Vérifier
ls notifications/

# Déplacer manuellement
mv notifications/*.txt notifications/sent/
```

### Erreur dans le cron

**Vérifier les logs :**
```bash
tail -50 logs/live.log
```

**Tester manuellement :**
```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
bash scripts/cron_with_notify.sh
```

---

## 📈 Historique des Alertes

Toutes les notifications envoyées sont archivées dans `notifications/sent/` avec timestamp.

**Voir l'historique :**
```bash
ls -lt notifications/sent/ | head -20
cat notifications/sent/signal_20260207_153000.txt
```

**Nettoyer l'historique (> 30 jours) :**
```bash
find notifications/sent/ -name "*.txt" -mtime +30 -delete
```

---

## 🎯 Exemples de Cas d'Usage

### Scénario 1 : Matin Calme

**15h30** → Cron analyse  
**Résultat** → Aucun signal (marché stable)  
**Action** → Log seulement, pas de notification

### Scénario 2 : Signal BUY Détecté

**15h30** → Cron analyse  
**Résultat** → NVDA score 6.2 (BUY signal)  
**Action** → Crée `notifications/signal_20260207_153000.txt`  
**16:00** → Heartbeat détecte le fichier  
**Action** → Envoie sur Telegram, déplace dans `sent/`

### Scénario 3 : Stop-Loss Déclenché

**15h30** → Cron analyse  
**Résultat** → AAPL à -5.2% (SELL signal STOP_LOSS)  
**Action** → Crée notification  
**François reçoit** → Alerte SELL avec P&L négatif

---

## ⚡ Alertes Temps Réel (Futur)

Actuellement : **1 fois par jour à 15h30**

Pour passer en temps réel (toutes les heures) :

```bash
crontab -e
```

Ajouter :
```cron
# Analyse toutes les heures pendant les heures de marché (15h-22h GMT+1)
0 15-22 * * 1-5 cd /home/pi/.openclaw/workspace/skills/market-analyzer && bash scripts/cron_with_notify.sh
```

**Note :** Plus de notifications = plus de bruit. Recommandé seulement après validation.

---

## 📝 Notes Importantes

1. **Paper Trading** : Les signaux sont basés sur le portfolio virtuel, pas de vrai argent
2. **Délai d'envoi** : Max 30 min entre création et envoi (délai heartbeat)
3. **Pas de spam** : 1 analyse = 1 notification max (même si plusieurs signaux)
4. **Archivage** : Toutes les notifications sont gardées dans `sent/`

---

✅ **Le système d'alertes est maintenant actif et testé !**

**Prochaine alerte automatique :** Lundi 10 février à 15h30 (ou aujourd'hui si avant 15h30)

🦎 **Bon trading !**
