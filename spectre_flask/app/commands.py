import click
from flask.cli import with_appcontext
from sqlalchemy import select

from .extensions import db
from .models import User, Role, Permission
from .utils.permissions import PERMISSIONS_INITIALES, ROLES_INITIAUX


DEFAULT_ADMIN_EMAIL = "admin@example.com"
ADMIN_EMAILS = (DEFAULT_ADMIN_EMAIL, "admin@spectre.local")


@click.command("seed")
@with_appcontext
def seed_command():
    """Créer les rôles, permissions et un compte administrateur par défaut."""

    permissions = {}
    for code, description in PERMISSIONS_INITIALES:
        permission = db.session.scalar(select(Permission).where(Permission.code == code))
        if permission is None:
            permission = Permission(code=code, description=description)
            db.session.add(permission)
        else:
            permission.description = description
        permissions[code] = permission

    for role_name, permission_codes in ROLES_INITIAUX.items():
        role = db.session.scalar(select(Role).where(Role.nom == role_name))
        if role is None:
            role = Role(nom=role_name, description=f"Rôle {role_name}")
            db.session.add(role)
        for code in permission_codes:
            permission = permissions[code]
            if permission not in role.permissions.all():
                role.permissions.append(permission)

    admin = db.session.scalar(select(User).where(User.email.in_(ADMIN_EMAILS)))
    if admin is None:
        admin = User(nom="Administrateur", prenom="Systeme", email=DEFAULT_ADMIN_EMAIL, actif=True)
        admin.set_password("admin123")
        db.session.add(admin)
    else:
        admin.email = DEFAULT_ADMIN_EMAIL

    admin_role = db.session.scalar(select(Role).where(Role.nom == "Administrateur"))
    if admin_role and admin_role not in admin.roles.all():
        admin.roles.append(admin_role)

    db.session.commit()
    click.echo(f"Données initiales créées. Compte : {DEFAULT_ADMIN_EMAIL} / admin123")
