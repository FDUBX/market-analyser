# Quick Start - Market Analyzer

## Premier lancement (demain matin)

### 1. Précharger les données (IMPORTANT!)

```bash
cd /home/pi/.openclaw/workspace/skills/market-analyzer
bash scripts/preload_data.sh
```

Cela va télécharger 2 ans de données historiques pour éviter le rate limit.
**Temps:** ~1-2 minutes

### 2. Créer un portfolio de test

Via dashboard: http://192.168.1.64:8080/simulator

Ou via CLI:
```bash
python3 scripts/portfolio_sim.py create \
  --name "Test 2024 Complet" \
  --capital 10000 \
  --start 2024-01-01
```

### 3. Lancer la simulation

Via dashboard: Cliquer sur "▶️ Run"

Ou via CLI:
```bash
python3 scripts/portfolio_sim.py run --id 1 --end 2024-12-31
```

**Avec le cache:** La simulation sera 10x plus rapide! (~10-15 secondes au lieu de 2 minutes)

### 4. Voir les résultats

Dashboard: http://192.168.1.64:8080/simulator/1

Tu devrais voir:
- Trades exécutés (grâce aux seuils ajustés: BUY 6.0 / SELL 4.5)
- Courbe de performance
- Positions ouvertes/fermées
- Métriques (Return %, Win Rate)

## Commandes utiles

**Voir le cache:**
```bash
python3 scripts/data_cache.py stats
```

**Analyser une action:**
```bash
python3 scripts/analyzer.py analyze AAPL
```

**Backtest:**
```bash
python3 scripts/backtest.py AAPL --period 1y
```

## Si problèmes

**Rate limit encore actif?**
→ Attendre quelques heures

**Pas de trades?**
→ Vérifier les seuils dans le code (devraient être BUY: 6.0, SELL: 4.5)

**Erreur de cache?**
→ `python3 scripts/data_cache.py clear` puis recharger

## Prochaines optimisations

Une fois que le système fonctionne:
1. Ajuster les seuils BUY/SELL selon résultats
2. Modifier les pondérations (technique/fondamental/sentiment)
3. Tester différents univers d'actions
4. Comparer plusieurs stratégies

---

🦎 Le cache résout le problème de rate limit définitivement!
