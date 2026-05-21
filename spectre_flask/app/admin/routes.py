from flask import Blueprint, render_template, redirect, url_for, flash
from sqlalchemy import select

from app.extensions import db
from app.models import User, Role, Permission, HistoriqueAction
from app.utils.permissions import permission_required, permission_label
from app.utils.audit import log_action
from .forms import UserForm, RoleForm


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users")
@permission_required("gerer_utilisateurs")
def users_index():
    users = db.session.scalars(select(User).order_by(User.nom.asc())).all()
    return render_template("admin/users_index.html", users=users)


@admin_bp.route("/users/create", methods=["GET", "POST"])
@permission_required("gerer_utilisateurs")
def users_create():
    form = UserForm()
    roles = db.session.scalars(select(Role).order_by(Role.nom.asc())).all()
    form.roles.choices = [(r.id, r.nom) for r in roles]
    if form.validate_on_submit():
        user = User(
            nom=form.nom.data,
            prenom=form.prenom.data,
            email=form.email.data.lower().strip(),
            actif=form.actif.data,
        )
        user.set_password(form.password.data or "password123")
        selected_roles = (
            db.session.scalars(select(Role).where(Role.id.in_(form.roles.data))).all()
            if form.roles.data
            else []
        )
        user.roles = selected_roles
        db.session.add(user)
        db.session.flush()
        log_action("Création utilisateur", entite="users", entite_id=user.id)
        db.session.commit()
        flash("Utilisateur créé.", "success")
        return redirect(url_for("admin.users_index"))
    return render_template("admin/user_form.html", form=form, title="Créer un utilisateur")


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@permission_required("gerer_utilisateurs")
def users_toggle(user_id):
    user = db.get_or_404(User, user_id)
    user.actif = not user.actif
    log_action("Activation/désactivation utilisateur", entite="users", entite_id=user.id)
    db.session.commit()
    flash("Statut du compte modifié.", "info")
    return redirect(url_for("admin.users_index"))


@admin_bp.route("/roles")
@permission_required("gerer_roles")
def roles_index():
    roles = db.session.scalars(select(Role).order_by(Role.nom.asc())).all()
    return render_template("admin/roles_index.html", roles=roles, permission_label=permission_label)


@admin_bp.route("/roles/create", methods=["GET", "POST"])
@permission_required("gerer_roles")
def roles_create():
    form = RoleForm()
    permissions = db.session.scalars(select(Permission).order_by(Permission.code.asc())).all()
    form.permissions.choices = [(p.id, permission_label(p.code)) for p in permissions]
    if form.validate_on_submit():
        role = Role(nom=form.nom.data.strip(), description=form.description.data)
        selected_permissions = (
            db.session.scalars(select(Permission).where(Permission.id.in_(form.permissions.data))).all()
            if form.permissions.data
            else []
        )
        role.permissions = selected_permissions
        db.session.add(role)
        db.session.flush()
        log_action("Création rôle", entite="roles", entite_id=role.id)
        db.session.commit()
        flash("Rôle créé.", "success")
        return redirect(url_for("admin.roles_index"))
    return render_template("admin/role_form.html", form=form, title="Créer un rôle")


@admin_bp.route("/roles/<int:role_id>/edit", methods=["GET", "POST"])
@permission_required("gerer_roles")
def roles_edit(role_id):
    role = db.get_or_404(Role, role_id)
    form = RoleForm(obj=role)
    permissions = db.session.scalars(select(Permission).order_by(Permission.code.asc())).all()
    form.permissions.choices = [(p.id, permission_label(p.code)) for p in permissions]
    if form.validate_on_submit():
        role.nom = form.nom.data.strip()
        role.description = form.description.data
        selected_permissions = (
            db.session.scalars(select(Permission).where(Permission.id.in_(form.permissions.data))).all()
            if form.permissions.data
            else []
        )
        role.permissions = selected_permissions
        log_action("Modification rôle", entite="roles", entite_id=role.id)
        db.session.commit()
        flash("Rôle modifié.", "success")
        return redirect(url_for("admin.roles_index"))
    form.permissions.data = [p.id for p in role.permissions.all()]
    return render_template("admin/role_form.html", form=form, title="Modifier un rôle")


@admin_bp.route("/journaux")
@permission_required("consulter_journaux")
def journaux():
    logs = db.session.scalars(
        select(HistoriqueAction).order_by(HistoriqueAction.date_action.desc()).limit(200)
    ).all()
    return render_template("admin/journaux.html", logs=logs)
