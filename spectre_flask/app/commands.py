import click
from flask.cli import with_appcontext

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
        permission = Permission.query.filter_by(code=code).first()
        if permission is None:
            permission = Permission(code=code, description=description)
            db.session.add(permission)
        permissions[code] = permission

    for role_name, permission_codes in ROLES_INITIAUX.items():
        role = Role.query.filter_by(nom=role_name).first()
        if role is None:
            role = Role(nom=role_name, description=f"Rôle {role_name}")
            db.session.add(role)
        for code in permission_codes:
            permission = permissions[code]
            if permission not in role.permissions.all():
                role.permissions.append(permission)

    admin = User.query.filter(User.email.in_(ADMIN_EMAILS)).first()
    if admin is None:
        admin = User(nom="Administrateur", prenom="Systeme", email=DEFAULT_ADMIN_EMAIL, actif=True)
        admin.set_password("admin123")
        db.session.add(admin)
    else:
        admin.email = DEFAULT_ADMIN_EMAIL

    admin_role = Role.query.filter_by(nom="Administrateur").first()
    if admin_role and admin_role not in admin.roles.all():
        admin.roles.append(admin_role)

    db.session.commit()
    click.echo(f"Donnees initiales creees. Compte : {DEFAULT_ADMIN_EMAIL} / admin123")
