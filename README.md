# Système de gestion des autorisations du spectre - Refonte V2

## Principe métier

Cette version introduit un nouvel acteur : **Utilisateur**.  
L'utilisateur représente une entreprise ou un organisme. Il peut créer son compte, mais il ne peut accéder au système qu'après validation par l'administrateur.

L'ancien rôle Responsable est fusionné avec **Agent**.  
L'Agent traite les demandes, demande des compléments, valide, rejette et génère les autorisations.

## Règle importante : rôle non modifiable

Après la création d'un compte, le changement de rôle est interdit.

Cette règle est appliquée dans le modèle `User` avec :

- `role_id`
- `role_locked=True`
- un événement SQLAlchemy `before_update` qui bloque toute modification de `role_id`.

L'administrateur peut valider, refuser ou suspendre un compte, mais il ne peut pas changer son rôle.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set FLASK_APP=run.py
flask db init
flask db migrate -m "initial database"
flask db upgrade
flask seed
flask seed-bandes
flask run
```

PowerShell :

```powershell
$env:FLASK_APP="run.py"
flask db init
flask db migrate -m "initial database"
flask db upgrade
flask seed
flask seed-bandes
flask run
```

## Comptes de test

- Administrateur : `admin@spectre.local` / `admin123`
- Agent : `agent@spectre.local` / `agent123`

## Scénario de démonstration

1. Un utilisateur crée un compte entreprise.
2. L'administrateur valide le compte.
3. L'utilisateur se connecte.
4. L'utilisateur soumet une demande.
5. L'utilisateur ajoute des pièces.
6. L'agent prend la demande en traitement.
7. L'agent demande un complément ou valide/rejette.
8. Si la demande est validée, l'agent génère l'autorisation.
9. L'utilisateur consulte l'état de la demande et l'autorisation.

## Remarque réglementaire

Les bandes de fréquence fournies dans `data/bandes_tnabf_demo.csv` servent à la démonstration.
Toute attribution réelle doit être vérifiée avec le Tableau National d'Attribution des Bandes de Fréquences et les documents officiels de l'Autorité de Régulation.


## Séparation des pages de connexion

La V2 sépare les accès en deux portails :

- `/connexion-utilisateur` : réservé aux entreprises et organismes utilisateurs ;
- `/connexion-interne` : réservé à l'Administrateur et à l'Agent ;
- `/connexion` : page de choix entre les deux espaces.

Un compte utilisateur externe est créé avec le rôle `Utilisateur`, le statut `en_attente` et `role_locked=True`. Après création, le changement de rôle est interdit par le modèle afin de préserver la séparation des responsabilités.

Les deux logos institutionnels sont placés dans l'en-tête :

- `app/static/img/logo_autorite_regulation.png` ;
- `app/static/img/logo_republique_mauritanie.svg`.
