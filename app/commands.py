import csv
from pathlib import Path
import click
from flask.cli import with_appcontext
from datetime import datetime

from .extensions import db
from .models import User, Role, Permission, BandeFrequence
from .utils.constants import ROLE_ADMIN, ROLE_AGENT, ROLE_UTILISATEUR, STATUT_COMPTE_VALIDE

PERMISSIONS = [
    ("valider_comptes", "Valider ou refuser les comptes utilisateurs"),
    ("gerer_agents", "Créer et gérer les agents"),
    ("gerer_bandes", "Gérer le référentiel des bandes"),
    ("consulter_journaux", "Consulter les journaux"),
    ("soumettre_demande", "Soumettre une demande"),
    ("suivre_mes_demandes", "Suivre ses demandes"),
    ("traiter_demande", "Traiter les demandes"),
    ("demander_complement", "Demander un complément"),
    ("valider_demande", "Valider une demande"),
    ("rejeter_demande", "Rejeter une demande"),
    ("generer_autorisation", "Générer une autorisation"),
]

ROLE_PERMISSIONS = {
    ROLE_ADMIN: ["valider_comptes", "gerer_agents", "gerer_bandes", "consulter_journaux"],
    ROLE_AGENT: ["traiter_demande", "demander_complement", "valider_demande", "rejeter_demande", "generer_autorisation", "gerer_bandes"],
    ROLE_UTILISATEUR: ["soumettre_demande", "suivre_mes_demandes"],
}

@click.command("seed")
@with_appcontext
def seed_command():
    permissions = {}
    for code, description in PERMISSIONS:
        permission = Permission.query.filter_by(code=code).first()
        if permission is None:
            permission = Permission(code=code, description=description)
            db.session.add(permission)
        permissions[code] = permission

    roles = {}
    for role_name, codes in ROLE_PERMISSIONS.items():
        role = Role.query.filter_by(nom=role_name).first()
        if role is None:
            role = Role(nom=role_name, description=f"Rôle {role_name}")
            db.session.add(role)
        for code in codes:
            if permissions[code] not in role.permissions.all():
                role.permissions.append(permissions[code])
        roles[role_name] = role

    admin = User.query.filter_by(email="admin@spectre.local").first()
    if admin is None:
        admin = User(
            nom="Administrateur",
            prenom="Système",
            email="admin@spectre.local",
            role=roles[ROLE_ADMIN],
            role_locked=True,
            statut_compte=STATUT_COMPTE_VALIDE,
            date_validation=datetime.utcnow(),
        )
        admin.set_password("admin123")
        db.session.add(admin)

    agent = User.query.filter_by(email="agent@spectre.local").first()
    if agent is None:
        agent = User(
            nom="Agent",
            prenom="Test",
            email="agent@spectre.local",
            role=roles[ROLE_AGENT],
            role_locked=True,
            statut_compte=STATUT_COMPTE_VALIDE,
            date_validation=datetime.utcnow(),
        )
        agent.set_password("agent123")
        db.session.add(agent)

    db.session.commit()
    click.echo("Données initiales créées.")
    click.echo("Admin : admin@spectre.local / admin123")
    click.echo("Agent : agent@spectre.local / agent123")

@click.command("seed-bandes")
@with_appcontext
def seed_bandes_command():
    csv_path = Path("data/bandes_tnabf_demo.csv")
    if not csv_path.exists():
        click.echo("Fichier data/bandes_tnabf_demo.csv introuvable.")
        return

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            existing = BandeFrequence.query.filter_by(designation=row["designation"]).first()
            if existing:
                continue
            bande = BandeFrequence(
                designation=row["designation"],
                frequence_debut=row["frequence_debut"],
                frequence_fin=row["frequence_fin"],
                unite=row["unite"],
                usage_service=row.get("usage_service"),
                statut=row.get("statut", "reference"),
                description=row.get("description"),
            )
            db.session.add(bande)
            count += 1
        db.session.commit()
    click.echo(f"{count} bande(s) importée(s).")
