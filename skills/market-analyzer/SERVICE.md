# Service Systemd - Market Analyzer Dashboard

Ce guide explique comment installer et gérer le dashboard comme service système qui démarre automatiquement.

---

## 🚀 Installation (Une seule fois)

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
sudo bash install_service.sh
```

**Ce que fait le script :**
- ✅ Arrête le dashboard s'il tourne déjà
- ✅ Crée le fichier service systemd
- ✅ Active le service au démarrage
- ✅ Démarre le service immédiatement
- ✅ Affiche le statut

---

## 📊 Vérifier le Statut

```bash
sudo systemctl status market-analyzer-dashboard
```

**Sortie attendue :**
```
● market-analyzer-dashboard.service - Market Analyzer Dashboard
   Loaded: loaded (/etc/systemd/system/market-analyzer-dashboard.service; enabled)
   Active: active (running) since ...
```

**Indicateurs :**
- `loaded` = Service installé ✅
- `enabled` = Démarrera au boot ✅
- `active (running)` = Tourne actuellement ✅

---

## 🎛️ Commandes de Gestion

### Démarrer le Service
```bash
sudo systemctl start market-analyzer-dashboard
```

### Arrêter le Service
```bash
sudo systemctl stop market-analyzer-dashboard
```

### Redémarrer le Service
```bash
sudo systemctl restart market-analyzer-dashboard
```

### Recharger Après Modification
```bash
sudo systemctl daemon-reload
sudo systemctl restart market-analyzer-dashboard
```

---

## 📝 Voir les Logs

### Logs en Temps Réel
```bash
sudo journalctl -u market-analyzer-dashboard -f
```

**Quitter :** `Ctrl + C`

### Logs Récents (100 dernières lignes)
```bash
sudo journalctl -u market-analyzer-dashboard -n 100
```

### Logs depuis le Boot
```bash
sudo journalctl -u market-analyzer-dashboard -b
```

### Logs dans un Fichier
```bash
tail -f /home/pi/.openclaw/workspace/skills/market-analyzer/logs/dashboard.log
```

---

## 🔧 Configuration Avancée

### Désactiver le Démarrage Automatique

Si tu veux que le dashboard ne démarre PAS automatiquement au boot :

```bash
sudo systemctl disable market-analyzer-dashboard
```

Il faudra alors le démarrer manuellement avec `systemctl start`.

### Réactiver le Démarrage Automatique

```bash
sudo systemctl enable market-analyzer-dashboard
```

### Modifier le Service

Éditer le fichier :
```bash
sudo nano /etc/systemd/system/market-analyzer-dashboard.service
```

Après modification :
```bash
sudo systemctl daemon-reload
sudo systemctl restart market-analyzer-dashboard
```

---

## 🔄 Redémarrage Automatique

Le service est configuré pour **redémarrer automatiquement** en cas de :
- Crash du dashboard
- Erreur Python
- Problème réseau temporaire

**Délai de redémarrage :** 10 secondes

**Configuration :**
```ini
Restart=always
RestartSec=10
```

---

## 🛡️ Sécurité

Le service est configuré avec des options de sécurité :

- `NoNewPrivileges=true` : Ne peut pas acquérir de nouveaux privilèges
- `PrivateTmp=true` : Utilise un répertoire /tmp isolé
- `User=pi` : Tourne avec l'utilisateur pi (pas root)

---

## 🐛 Troubleshooting

### Le service ne démarre pas

**Vérifier les erreurs :**
```bash
sudo journalctl -u market-analyzer-dashboard -n 50
```

**Causes communes :**
- Port 8080 déjà utilisé
- Dépendances Python manquantes
- Permissions incorrectes

**Tester manuellement :**
```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer/scripts
python3 dashboard_advanced.py
```

### Port 8080 déjà utilisé

**Trouver le processus :**
```bash
sudo lsof -i :8080
```

**Tuer le processus :**
```bash
sudo kill -9 <PID>
```

Puis redémarrer le service.

### Dépendances manquantes

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
pip3 install -r requirements.txt
```

### Le dashboard est lent

**Vérifier la charge système :**
```bash
htop
```

**Vérifier la mémoire :**
```bash
free -h
```

Si le Raspberry Pi manque de RAM, envisager :
- Réduire le nombre de portfolios
- Nettoyer le cache
- Redémarrer le système

---

## 📈 Monitoring

### Vérifier que le Dashboard Répond

```bash
curl -I http://192.168.1.64:8080/live
```

**Sortie attendue :**
```
HTTP/1.1 200 OK
```

### Script de Health Check

Créer un script de monitoring :

```bash
#!/bin/bash
if ! curl -s http://localhost:8080/live > /dev/null; then
    echo "Dashboard down! Restarting..."
    sudo systemctl restart market-analyzer-dashboard
fi
```

Ajouter à cron pour vérification toutes les 5 minutes :
```cron
*/5 * * * * /home/pi/check_dashboard.sh
```

---

## 🗑️ Désinstallation

Pour supprimer complètement le service :

```bash
# Arrêter et désactiver
sudo systemctl stop market-analyzer-dashboard
sudo systemctl disable market-analyzer-dashboard

# Supprimer le fichier service
sudo rm /etc/systemd/system/market-analyzer-dashboard.service

# Recharger systemd
sudo systemctl daemon-reload
```

Les données et fichiers du Market Analyzer restent intacts.

---

## 📊 Informations Système

**Fichier service :**
```
/etc/systemd/system/market-analyzer-dashboard.service
```

**Répertoire de travail :**
```
/home/pi/.openclaw/workspace/skills/market-analyzer/scripts
```

**Logs :**
```
/home/pi/.openclaw/workspace/skills/market-analyzer/logs/dashboard.log
```

**Port :**
```
8080 (TCP)
```

**URL d'accès :**
```
http://192.168.1.64:8080
```

---

## ✅ Checklist Post-Installation

- [ ] Service installé : `systemctl status market-analyzer-dashboard`
- [ ] Dashboard accessible : http://192.168.1.64:8080
- [ ] Onglet Live fonctionne : http://192.168.1.64:8080/live
- [ ] Logs visibles : `journalctl -u market-analyzer-dashboard`
- [ ] Redémarrage automatique configuré
- [ ] Service activé au boot

---

🦎 **Le dashboard tournera maintenant en permanence et redémarrera automatiquement après un reboot !**
