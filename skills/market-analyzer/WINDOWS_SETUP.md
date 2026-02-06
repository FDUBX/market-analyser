# Installation sur Windows

## 1. Installer Python

Python n’est pas installé par défaut sur Windows. Deux options :

### Option A – Microsoft Store (simple)

1. Ouvre **PowerShell** ou l’**invite de commandes**.
2. Tape : `python`
3. Windows propose d’ouvrir le **Microsoft Store** sur la page Python → clique sur **Obtenir** / **Installer**.
4. Une fois l’installation terminée, **ferme et rouvre** PowerShell.
5. Vérifie : `python --version` (tu dois voir une version, ex. 3.12).

### Option B – python.org (recommandé pour le dev)

1. Va sur **https://www.python.org/downloads/**
2. Télécharge **Python 3.12** (ou la dernière version 3.x).
3. Lance l’installateur.
4. **Important** : coche **“Add python.exe to PATH”** en bas de la première fenêtre.
5. Clique sur **Install Now**, puis ferme et rouvre PowerShell.
6. Vérifie : `python --version` et `pip --version`.

---

## 2. Installer les dépendances du Market Analyzer

Dans PowerShell, à la racine du repo :

```powershell
cd skills\market-analyzer
python -m pip install -r requirements.txt
```

(Si tu as installé via le Store, la commande peut être `python3` ou `py` à la place de `python`.)

---

## 3. Lancer le dashboard

```powershell
.\scripts\run_dashboard.ps1
```

Ou :

```powershell
python scripts\dashboard_advanced.py --port 8080
```

Puis ouvre **http://localhost:8080** dans ton navigateur.
