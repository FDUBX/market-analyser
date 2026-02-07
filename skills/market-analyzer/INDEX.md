# Market Analyzer - Index 📚

## 📂 Documentation Complète

### Pour Démarrer
- **[QUICKSTART.md](QUICKSTART.md)** - Démarrage rapide (5 minutes)
- **[README_COMPLETE.md](README_COMPLETE.md)** - Guide complet et détaillé

### Configuration Actuelle
- **[OPTIMIZATION_RESULTS.md](OPTIMIZATION_RESULTS.md)** ⭐ **LIRE EN PREMIER**
  - Configuration optimale validée (v2.1)
  - Résultats 2023-2025
  - +33.27% return annuel moyen

### Technique
- **[SKILL.md](SKILL.md)** - Documentation technique OpenClaw
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Historique des améliorations
- **[README.md](README.md)** - Description basique

---

## ⚙️ Configuration Actuelle (OPTIMISÉE)

**Stratégie par défaut :** Balanced Optimisé (v2.1)

```json
{
  "buy_threshold": 5.5,
  "sell_threshold": 4.5,
  "stop_loss": 0.05,
  "take_profit": 0.18,
  "weights": {
    "technical": 0.4,
    "fundamental": 0.4,
    "sentiment": 0.2
  }
}
```

**Performance validée (2023-2025) :**
- 2023: +52.29%
- 2024: +33.57%
- 2025: +13.93%
- **Moyenne: +33.27%**

---

## 🚀 Quick Start

```bash
# 1. Précharger les données (une fois)
bash scripts/preload_data.sh

# 2. Lancer le dashboard
python3 scripts/dashboard_advanced.py --port 8080

# 3. Ouvrir dans le navigateur
http://192.168.1.64:8080
```

---

## 📊 Fichiers Importants

### Configuration
- `config.json` - Config globale (seuils optimisés)
- `strategies.json` - 5 stratégies prédéfinies

### Scripts
- `analyzer.py` - Analyse multi-dimensionnelle
- `portfolio_sim.py` - Simulateur de trading
- `backtest.py` - Backtesting moteur
- `data_cache.py` - Cache local (évite rate limits)
- `optimizer.py` - Optimisation automatique
- `dashboard_advanced.py` - Interface web FastAPI + Chart.js

### Bases de Données
- `portfolio_sim.db` - Portfolios et trades
- `data_cache.db` - Cache des données historiques

---

## 🎯 Stratégies Disponibles

1. **Balanced Optimisé** ⭐ (recommandé, v2.1)
   - BUY 5.5 / SELL 4.5
   - TP 18% / SL 5%
   - Return: +33.27% moyen (3 ans)

2. **Aggressive**
   - BUY 5.5 / SELL 5.0
   - TP 20% / SL 7%
   - Return: +20% (2024)

3. **Conservative**
   - BUY 7.0 / SELL 4.0
   - TP 10% / SL 5%
   - Moins de trades, plus sûr

4. **Momentum**
   - Focus technique (70%)
   - Suit les tendances

5. **Value**
   - Focus fondamental (60%)
   - Investissement long terme

---

## 📈 Utilisation

### Via Dashboard (Recommandé)
1. Aller sur http://192.168.1.64:8080/strategies
2. Choisir "Balanced Optimisé"
3. Créer portfolio avec $10,000
4. Date: 2024-01-01
5. Lancer simulation
6. Voir résultats avec graphiques Chart.js

### Via CLI
```bash
# Créer portfolio
python3 scripts/portfolio_sim.py create \
  --name "Mon Portfolio" \
  --capital 10000 \
  --start 2024-01-01

# Lancer simulation
python3 scripts/portfolio_sim.py run --id 1 --end 2024-12-31

# Analyser une action
python3 scripts/analyzer.py analyze AAPL
```

---

## 🔧 Maintenance

**Quotidienne :** Rien (automatique avec cache)

**Hebdomadaire :**
```bash
# Mettre à jour le cache
bash scripts/preload_data.sh
```

**Mensuelle :**
- Vérifier performance des portfolios actifs
- Ajuster si nécessaire

**Trimestrielle :**
- Backtester sur période récente
- Comparer avec Balanced Optimisé

**Annuelle :**
- Ré-optimiser avec `optimizer.py`
- Valider nouvelle config

---

## 📞 Support

- **Documentation technique :** SKILL.md
- **Guide complet :** README_COMPLETE.md
- **Résultats optimisation :** OPTIMIZATION_RESULTS.md
- **Quick start :** QUICKSTART.md

---

## ✅ Checklist Nouveau Déploiement

- [ ] Installer dépendances : `bash scripts/install_deps.sh`
- [ ] Précharger données : `bash scripts/preload_data.sh`
- [ ] Vérifier config : `cat config.json`
- [ ] Lancer dashboard : `python3 scripts/dashboard_advanced.py --port 8080`
- [ ] Tester analyse : `python3 scripts/analyzer.py analyze AAPL`
- [ ] Créer portfolio test
- [ ] Lancer simulation
- [ ] Vérifier résultats

---

🦎 **Market Analyzer v2.1 - Optimisé et Validé**

Dernière mise à jour : 2026-02-07
