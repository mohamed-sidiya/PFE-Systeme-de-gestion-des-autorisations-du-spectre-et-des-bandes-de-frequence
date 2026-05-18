# Système de gestion des autorisations du spectre et des bandes de fréquence

Prototype Flask pour un projet de fin d'études.

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Initialisation

```bash
set FLASK_APP=run.py        # Windows CMD
# ou PowerShell : $env:FLASK_APP="run.py"
# ou Linux/macOS : export FLASK_APP=run.py

flask db upgrade
flask seed
flask run
```

Compte créé par défaut après `flask seed` :

- Email : `admin@example.com`
- Mot de passe : `admin123`

## Remarque

Le modèle reste volontairement extensible : les statuts, rôles, permissions, types de demandes et pièces obligatoires peuvent être adaptés après validation auprès de l'Autorité de Régulation.
