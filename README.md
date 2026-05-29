# Systeme de gestion des autorisations du spectre - V2

## Principe metier

Cette application gere les demandes d'autorisation d'utilisation des bandes de frequences radioelectriques.

Trois profils sont separes :

- **Utilisateur** : entreprise ou organisme demandeur.
- **Administrateur** : valide les comptes, verifie le NIF, gere les agents et les journaux.
- **Agent** : instruit les demandes, genere les factures, valide/rejette et genere les autorisations.

Le role d'un compte est fixe a la creation et ne peut pas etre modifie ensuite.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set FLASK_APP=run.py
flask db upgrade
flask seed
flask seed-bandes
flask run
```

PowerShell :

```powershell
$env:FLASK_APP="run.py"
flask db upgrade
flask seed
flask seed-bandes
flask run
```

## Comptes de test

- Administrateur : `admin@spectre.local` / `admin123`
- Agent : `agent@spectre.local` / `agent123`

## Portails de connexion

- Utilisateur : `/connexion-utilisateur`
- Administrateur : `/connexion-admin`
- Agent : `/connexion-agent`

Chaque portail utilise une session separee en environnement local, ce qui permet de tester les trois profils dans le meme navigateur.

## Workflow de demonstration

1. Un utilisateur cree un compte entreprise.
2. L'administrateur valide le compte et peut verifier le NIF.
3. L'utilisateur se connecte et soumet une nouvelle demande avec son dossier PDF.
4. L'agent prend la demande en traitement.
5. L'agent peut demander un complement, rejeter, ou generer une facture.
6. L'utilisateur consulte la facture, la telecharge en PDF, puis marque la facture comme payee.
7. L'agent voit le paiement, valide la demande, puis genere l'autorisation.
8. L'utilisateur telecharge l'autorisation en PDF.

## Remarque reglementaire

Les bandes de frequence fournies dans `data/bandes_tnabf_demo.csv` servent a la demonstration.
Toute attribution reelle doit etre verifiee avec le Tableau National d'Attribution des Bandes de Frequences et les documents officiels de l'Autorite de Regulation.

## Logos

Les logos institutionnels sont places dans l'en-tete :

- `app/static/img/logo_autorite_regulation.png`
- `app/static/img/logo_republique_mauritanie.svg`
