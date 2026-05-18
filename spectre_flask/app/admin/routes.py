from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import User, Role, HistoriqueAction
from app.utils.permissions import permission_required
from app.utils.audit import log_action
from .forms import UserForm


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users")
@permission_required("gerer_utilisateurs")
def users_index():
    users = User.query.order_by(User.nom.asc()).all()
    return render_template("admin/users_index.html", users=users)


@admin_bp.route("/users/create", methods=["GET", "POST"])
@permission_required("gerer_utilisateurs")
def users_create():
    form = UserForm()
    roles = Role.query.order_by(Role.nom.asc()).all()
    form.roles.choices = [(r.id, r.nom) for r in roles]
    if form.validate_on_submit():
        user = User(
            nom=form.nom.data,
            prenom=form.prenom.data,
            email=form.email.data.lower().strip(),
            actif=form.actif.data,
        )
        user.set_password(form.password.data or "password123")
        selected_roles = Role.query.filter(Role.id.in_(form.roles.data)).all() if form.roles.data else []
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
    user = User.query.get_or_404(user_id)
    user.actif = not user.actif
    log_action("Activation/désactivation utilisateur", entite="users", entite_id=user.id)
    db.session.commit()
    flash("Statut du compte modifié.", "info")
    return redirect(url_for("admin.users_index"))


@admin_bp.route("/journaux")
@permission_required("consulter_journaux")
def journaux():
    logs = HistoriqueAction.query.order_by(HistoriqueAction.date_action.desc()).limit(200).all()
    return render_template("admin/journaux.html", logs=logs)
