# Plan d'Optimisation v2.0 → v2.1

## 📊 Résultats Observés (v2.0)

### Performance Multi-Périodes

| Période | v1.0 | v2.0 | Δ | Trades v1.0 | Trades v2.0 |
|---------|------|------|---|-------------|-------------|
| **2024** | +32.47% | +32.38% | -0.09% | 82 | 108 |
| **2025** | +10.83% | +10.54% | -0.29% | 126 | 140 |
| **Moyenne** | **+21.65%** | **+21.46%** | **-0.19%** | 104 | 124 |

### Problèmes Identifiés

1. **Sur-trading** (+19% de trades)
   - Nouveaux indicateurs augmentent les scores
   - Plus de faux signaux BUY
   - Impact négatif si frais de transaction

2. **Return légèrement inférieur** (-0.2%)
   - Différence minime mais constante
   - Probablement lié au sur-trading

3. **Pondération égale non optimale**
   - Tous les indicateurs ont le même poids
   - Certains sont peut-être plus prédictifs

## 🎯 Optimisations Proposées

### Option 1: Pondération Intelligente des Indicateurs ⭐⭐⭐⭐⭐

**Problème:** Actuellement `np.mean(scores)` donne le même poids à tous

**Solution:** Pondérer selon importance historique

```python
# Dans _calculate_technical_score()
scores_weighted = {
    'rsi': (rsi_score, 0.20),          # Core indicator
    'macd': (macd_score, 0.18),        # Trend confirmation
    'bollinger': (bb_score, 0.15),     # Volatility
    'trend': (trend_score, 0.15),      # SMA crossover
    'volume': (vol_score, 0.12),       # Volume confirmation
    'adx': (adx_score, 0.08),          # Trend strength (new)
    'williams': (willr_score, 0.06),   # Momentum (new)
    'obv': (obv_score, 0.03),          # Volume trend (new)
    '52w_pos': (pos_52w_score, 0.03),  # Support/resistance (new)
}

total_score = sum(score * weight for score, weight in scores_weighted.values())
```

**Impact Attendu:**
- Réduction du sur-trading (-10% trades)
- Amélioration return (+0.3% à +0.5%)
- Meilleure qualité de signaux

---

### Option 2: Ajuster les Seuils BUY/SELL ⭐⭐⭐

**Problème:** Seuils actuels (BUY 5.3, SELL 4.3) créés pour 5 indicateurs

**Solution:** Recalibrer pour 8 indicateurs

```json
{
  "thresholds": {
    "buy": 5.6,      // Était 5.3 (+0.3)
    "sell": 4.6      // Était 4.3 (+0.3)
  }
}
```

**Rationale:**
- Avec 8 indicateurs, scores moyens augmentent
- Hausser seuils = filtrer mieux
- Revenir au nombre de trades v1.0

**Impact Attendu:**
- Trades: 124 → ~100 (-19%)
- Return: +21.46% → +22%+ (+0.5%+)

---

### Option 3: Indicateurs Conditionnels ⭐⭐⭐⭐

**Problème:** Certains indicateurs peu fiables sur faibles volumes

**Solution:** N'utiliser ADX, Williams %R que si conditions favorables

```python
# ADX seulement si volume > moyenne
if hist['Volume'].iloc[-1] > hist['Volume'].mean():
    scores.append(adx_score)

# Williams %R seulement si ADX > 25 (tendance forte)
if adx > 25:
    scores.append(willr_score)
```

**Impact Attendu:**
- Réduction faux signaux
- Amélioration qualité trades
- Return stable ou légèrement meilleur

---

### Option 4: Stop-Loss Dynamique ⭐⭐⭐

**Problème:** Stop-loss fixe 5% ne s'adapte pas à la volatilité

**Solution:** Stop-loss basé sur ATR (Average True Range)

```python
# Dans portfolio_sim.py
atr = calculate_atr(hist, period=14)
dynamic_stop_loss = 2 * atr / current_price  # 2x ATR

# Valeurs typiques: 3-8% selon volatilité
stop_loss_pct = max(0.03, min(0.08, dynamic_stop_loss))
```

**Impact Attendu:**
- Moins de stops prématurés sur actions volatiles
- Meilleure protection sur actions stables
- Win rate +2-5%

---

### Option 5: Take-Profit Progressif ⭐⭐

**Problème:** Take-profit fixe 18% peut laisser passer de gros gains

**Solution:** Take-profit en 2 étapes

```python
# 50% position @ +12%
if pnl_pct >= 0.12:
    sell_half()

# 50% restant @ +20%
if pnl_pct >= 0.20:
    sell_remaining()
```

**Impact Attendu:**
- Capture gains rapides
- Laisse courir les winners
- Return +0.5-1%

---

## 🔬 Plan de Test

### Phase 1: Validation Pondération (Priorité 1)

1. Implémenter pondération intelligente
2. Tester sur 2023, 2024, 2025
3. Comparer vs v2.0
4. **Critère de succès:** Return ≥ v2.0 ET trades ≤ 110

### Phase 2: Ajustement Seuils (Priorité 2)

1. Tester seuils 5.4, 5.5, 5.6, 5.7
2. Identifier optimal
3. **Critère de succès:** Return ≥ +22% moyen

### Phase 3: Features Avancées (Priorité 3)

1. Indicateurs conditionnels
2. Stop-loss dynamique
3. **Critère de succès:** Win rate ≥ 60%

---

## 📊 KPIs de Validation

Pour chaque optimisation, mesurer:

| KPI | v2.0 Baseline | Target v2.1 |
|-----|---------------|-------------|
| **Return annuel moyen** | +21.46% | **≥ +22%** |
| **Nombre de trades** | 124 | **≤ 110** |
| **Win rate** | ~55% | **≥ 58%** |
| **Max drawdown** | TBD | **≤ -15%** |
| **Sharpe ratio** | TBD | **≥ 1.2** |

---

## 🚀 Implémentation Recommandée

**Ordre:**
1. ✅ Pondération intelligente (quick win, low risk)
2. ✅ Ajustement seuils (validation facile)
3. ⏸️ Features avancées (si besoin après 1-2)

**Timeline:**
- Phase 1: 30 min (code) + 1h (tests)
- Phase 2: 15 min (code) + 45 min (tests)
- Phase 3: 1-2h (si nécessaire)

---

## 📝 Notes

- Garder v2.0 comme fallback
- Documenter chaque changement
- Créer v2.1 branch si Git workflow

**Dernière mise à jour:** 2026-02-06
