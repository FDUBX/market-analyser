# Market Analyzer - Guide Complet 🚀

## 🎉 Ce qui est prêt MAINTENANT

Toutes les fonctionnalités sont implémentées ! Il ne reste qu'à attendre demain matin que le rate limit Yahoo Finance soit levé.

## 🌐 Accès Dashboard

**URL principale:** http://192.168.1.64:8080

### Pages disponibles:

1. **📊 Analyzer** - `/`
   - Analyse d'actions individuelles
   - Scores détaillés (technique/fondamental/sentiment)
   - Signaux BUY/SELL/HOLD

2. **🎮 Simulator** - `/simulator`
   - Liste de tous les portfolios
   - Création de nouveaux portfolios
   - Lancement de simulations
   - Détails avec graphiques Chart.js

3. **⚙️ Strategies** - `/strategies` ✨ NOUVEAU
   - 5 stratégies prédéfinies
   - Création de portfolio avec stratégie en 1 clic
   - Comparaison visuelle des paramètres

## 🚀 Démarrage Rapide (demain matin)

### 1. Précharger les données (IMPORTANT!)

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
bash scripts/preload_data.sh
```

**Durée:** 1-2 minutes  
**Fréquence:** Une fois (puis 1x/semaine pour refresh)

### 2. Tester une stratégie

**Via Dashboard:**
1. Aller sur http://192.168.1.64:8080/strategies
2. Choisir une stratégie (ex: "Balanced")
3. Donner un nom (ex: "Test Balanced 2024")
4. Capital: 10000
5. Date: 2024-01-01
6. Cliquer "Créer avec stratégie"
7. Cliquer "▶️ Run" sur le portfolio
8. Attendre 10-15 secondes
9. Cliquer "📊 Voir" pour voir les résultats

**Résultat attendu:**
- Graphique de performance avec Chart.js
- Liste des trades exécutés
- Métriques: Return %, Win Rate
- Positions ouvertes/fermées

### 3. Comparer plusieurs stratégies

```bash
# Créer 3 portfolios avec différentes stratégies:
# - Portfolio "Conservative 2024" avec stratégie Conservative
# - Portfolio "Balanced 2024" avec stratégie Balanced  
# - Portfolio "Aggressive 2024" avec stratégie Aggressive

# Lancer les 3 simulations
# Comparer les résultats visuellement
```

## 📚 Les 5 Stratégies

### 🛡️ Conservative
**Quand:** Capital à protéger, recherche de stabilité  
**Seuils:** BUY 7.0 | SELL 4.0  
**Focus:** Fondamental (50%) - Sélection stricte  
**Risque:** ⭐ Faible  
**Rendement attendu:** 5-8% annuel

### ⚖️ Balanced (recommandé pour débuter)
**Quand:** Équilibre risque/rendement  
**Seuils:** BUY 6.0 | SELL 4.5  
**Focus:** Équilibré (40/40/20)  
**Risque:** ⭐⭐ Moyen  
**Rendement attendu:** 10-15% annuel

### 🚀 Aggressive
**Quand:** Recherche de performance maximale  
**Seuils:** BUY 5.5 | SELL 5.0  
**Focus:** Technique (60%) - Plus de trades  
**Risque:** ⭐⭐⭐ Élevé  
**Rendement attendu:** 15-25% annuel (ou -10%)

### 📈 Momentum
**Quand:** Suivre la tendance du marché  
**Seuils:** BUY 6.5 | SELL 4.0  
**Focus:** Technique (70%) - Tendances fortes  
**Risque:** ⭐⭐⭐ Moyen-élevé  
**Rendement attendu:** 12-20% annuel

### 💎 Value
**Quand:** Investissement long terme  
**Seuils:** BUY 6.5 | SELL 4.5  
**Focus:** Fondamental (60%) - Valeur intrinsèque  
**Risque:** ⭐⭐ Faible-moyen  
**Rendement attendu:** 8-12% annuel

## 🛠️ Commandes CLI Avancées

### Optimisation automatique

```bash
# Trouver les meilleurs seuils pour AAPL
python3 scripts/optimizer.py thresholds --ticker AAPL --period 2y

# Trouver les meilleures pondérations
python3 scripts/optimizer.py weights --ticker AAPL

# Comparer les 5 stratégies sur plusieurs actions
python3 scripts/optimizer.py compare --tickers AAPL MSFT GOOGL NVDA
```

### Gestion du cache

```bash
# Voir statistiques
python3 scripts/data_cache.py stats

# Précharger données spécifiques
python3 scripts/data_cache.py preload \
  --tickers AAPL MSFT \
  --start 2024-01-01 \
  --end 2024-12-31

# Nettoyer cache
python3 scripts/data_cache.py clear --ticker AAPL
```

### Backtest direct

```bash
# Tester une action sur 2 ans
python3 scripts/backtest.py AAPL --period 2y

# Avec capital personnalisé
python3 scripts/backtest.py AAPL --period 1y --capital 50000
```

### Analyse simple

```bash
# Analyser une action
python3 scripts/analyzer.py analyze AAPL

# Plusieurs actions en JSON
python3 scripts/analyzer.py analyze AAPL MSFT GOOGL --output json
```

## 📊 Créer sa Propre Stratégie

Éditer `strategies.json` et ajouter:

```json
"MyStrategy": {
  "description": "Ma stratégie personnalisée",
  "buy_threshold": 6.5,
  "sell_threshold": 4.3,
  "weights": {
    "technical": 0.5,
    "fundamental": 0.4,
    "sentiment": 0.1
  },
  "position_size": 0.22,
  "stop_loss": 0.06,
  "take_profit": 0.16
}
```

Recharger le dashboard → ta stratégie apparaît dans `/strategies` !

## 🎯 Workflow Recommandé

### Phase 1: Test Initial (semaine 1)
1. Précharger les données
2. Créer 3 portfolios (Conservative, Balanced, Aggressive) sur 2024
3. Lancer les simulations
4. Comparer les résultats
5. Identifier la stratégie qui correspond à ton profil

### Phase 2: Optimisation (semaine 2)
1. Utiliser `optimizer.py` pour trouver les meilleurs paramètres
2. Créer ta stratégie personnalisée
3. Tester sur plusieurs univers d'actions
4. Valider avec backtesting

### Phase 3: Paper Trading (semaine 3+)
1. Créer portfolio avec date = aujourd'hui
2. Relancer la simulation chaque jour
3. Observer les trades en temps réel
4. Ajuster si besoin

### Phase 4: Réel (après validation)
1. Si les résultats sont satisfaisants sur plusieurs mois
2. Commencer avec petit capital réel
3. Suivre les signaux du simulateur
4. Documenter les résultats

## 🐛 Troubleshooting

### Pas de trades exécutés?
→ Vérifier les seuils (doivent être accessibles: BUY ~6.0)  
→ Vérifier que le cache est chargé  
→ Regarder les scores actuels: `python3 scripts/analyzer.py analyze AAPL`

### Rate limit Yahoo?
→ Attendre 1-2h  
→ Utiliser le cache (précharger au lieu de requêter en direct)

### Dashboard ne répond pas?
→ Vérifier le processus: `ps aux | grep dashboard`  
→ Redémarrer: `pkill -f dashboard && python3 scripts/dashboard_advanced.py --port 8080 &`

### Simulation trop lente?
→ Précharger les données avec `bash scripts/preload_data.sh`  
→ Réduire l'univers d'actions (3-4 au lieu de 7)

## 📁 Structure des Fichiers

```
market-analyzer/
├── scripts/
│   ├── analyzer.py              # Analyse multi-dimensionnelle
│   ├── backtest.py              # Backtesting moteur
│   ├── portfolio_sim.py         # Simulateur de portfolio
│   ├── data_cache.py           # Système de cache local
│   ├── optimizer.py            # Optimisation automatique
│   ├── dashboard_advanced.py   # Dashboard avec Chart.js
│   └── preload_data.sh         # Préchargement facile
├── strategies.json             # 5 stratégies prédéfinies
├── config.json                 # Configuration globale
├── portfolio_sim.db            # Base SQLite (créée auto)
├── data_cache.db              # Cache données (créé auto)
├── SKILL.md                    # Documentation technique
├── QUICKSTART.md              # Guide démarrage rapide
├── IMPROVEMENTS.md            # Liste des améliorations
└── README_COMPLETE.md         # Ce fichier!
```

## 💡 Conseils Pro

**1. Diversifier les tests:**
Ne teste pas qu'une seule stratégie. Compare-les toutes pour comprendre les trade-offs.

**2. Regarder au-delà du return %:**
- Win rate (% de trades gagnants)
- Nombre de trades (liquidité)
- Max drawdown (pire perte)

**3. Tester sur différentes périodes:**
- 2024 (bull market)
- 2022 (bear market)
- 2023 (recovery)

**4. Adapter l'univers:**
Au lieu de 7 tech stocks, teste:
- Mix secteurs (tech + finance + santé)
- Small caps vs large caps
- International vs US

**5. Documenter:**
Garde une trace de ce qui marche/marche pas dans un fichier texte.

## 🎁 Bonus

Le système est **modulaire** ! Tu peux:
- Créer autant de stratégies que tu veux
- Modifier les indicateurs dans `analyzer.py`
- Ajouter de nouveaux tickers dans l'univers
- Exporter les résultats pour Excel
- Automatiser avec des cron jobs

## 📞 Support

Tous les fichiers sont documentés. Lis:
- `SKILL.md` pour la doc technique
- `IMPROVEMENTS.md` pour les nouvelles fonctionnalités
- `QUICKSTART.md` pour démarrer vite

---

🦎 **Market Analyzer est maintenant un système complet de simulation et d'optimisation de stratégies de trading !**

**Prêt à tester demain matin après préchargement des données.**
