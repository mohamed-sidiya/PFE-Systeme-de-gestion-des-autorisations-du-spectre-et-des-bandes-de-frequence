from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy import select
from flask_login import current_user

from app.extensions import db
from app.models import User, Role, HistoriqueAction
from app.utils.constants import ROLE_ADMIN, ROLE_AGENT, STATUT_COMPTE_ATTENTE, STATUT_COMPTE_VALIDE, STATUT_COMPTE_REFUSE, STATUT_COMPTE_SUSPENDU
from app.utils.decorators import role_required
from app.utils.audit import log_action
from .forms import AgentForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@role_required(ROLE_ADMIN)
def index():
    return redirect(url_for("admin.comptes"))

@admin_bp.route("/comptes")
@role_required(ROLE_ADMIN)
def comptes():
    statut = request.args.get("statut")
    query = select(User).order_by(User.date_creation.desc())
    if statut:
        query = query.where(User.statut_compte == statut)
    users = db.session.scalars(query).all()
    return render_template("admin/comptes.html", users=users, statut=statut)

@admin_bp.route("/comptes/<int:user_id>")
@role_required(ROLE_ADMIN)
def compte_detail(user_id):
    user = db.get_or_404(User, user_id)
    return render_template("admin/compte_detail.html", user=user)

@admin_bp.route("/comptes/<int:user_id>/valider", methods=["POST"])
@role_required(ROLE_ADMIN)
def valider_compte(user_id):
    user = db.get_or_404(User, user_id)
    user.statut_compte = STATUT_COMPTE_VALIDE
    user.date_validation = datetime.now(timezone.utc)
    user.valide_par_id = current_user.id
    log_action("Validation compte utilisateur", entite="users", entite_id=user.id)
    db.session.commit()
    flash("Compte validé. Le rôle n'a pas été modifié.", "success")
    return redirect(url_for("admin.compte_detail", user_id=user.id))

@admin_bp.route("/comptes/<int:user_id>/refuser", methods=["POST"])
@role_required(ROLE_ADMIN)
def refuser_compte(user_id):
    user = db.get_or_404(User, user_id)
    user.statut_compte = STATUT_COMPTE_REFUSE
    log_action("Refus compte utilisateur", entite="users", entite_id=user.id)
    db.session.commit()
    flash("Compte refusé.", "info")
    return redirect(url_for("admin.compte_detail", user_id=user.id))

@admin_bp.route("/comptes/<int:user_id>/verifier-nif", methods=["POST"])
@role_required(ROLE_ADMIN)
def verifier_nif(user_id):
    user = db.get_or_404(User, user_id)
    if not user.profil or not user.profil.identifiant:
        flash("Aucun NIF n'est renseigne pour ce compte.", "warning")
        return redirect(url_for("admin.compte_detail", user_id=user.id))

    user.profil.nif_verifie = True
    user.profil.nif_verifie_par_id = current_user.id
    user.profil.date_verification_nif = datetime.now(timezone.utc)
    log_action("Verification NIF", entite="profils_utilisateurs", entite_id=user.profil.id)
    db.session.commit()
    flash("NIF verifie.", "success")
    return redirect(url_for("admin.compte_detail", user_id=user.id))

@admin_bp.route("/comptes/<int:user_id>/annuler-verification-nif", methods=["POST"])
@role_required(ROLE_ADMIN)
def annuler_verification_nif(user_id):
    user = db.get_or_404(User, user_id)
    if not user.profil:
        flash("Aucun profil n'est associe a ce compte.", "warning")
        return redirect(url_for("admin.compte_detail", user_id=user.id))

    user.profil.nif_verifie = False
    user.profil.nif_verifie_par_id = None
    user.profil.date_verification_nif = None
    log_action("Annulation verification NIF", entite="profils_utilisateurs", entite_id=user.profil.id)
    db.session.commit()
    flash("Verification NIF annulee.", "info")
    return redirect(url_for("admin.compte_detail", user_id=user.id))

@admin_bp.route("/comptes/<int:user_id>/suspendre", methods=["POST"])
@role_required(ROLE_ADMIN)
def suspendre_compte(user_id):
    user = db.get_or_404(User, user_id)
    user.statut_compte = STATUT_COMPTE_SUSPENDU
    log_action("Suspension compte utilisateur", entite="users", entite_id=user.id)
    db.session.commit()
    flash("Compte suspendu.", "warning")
    return redirect(url_for("admin.comptes"))

@admin_bp.route("/agents")
@role_required(ROLE_ADMIN)
def agents():
    agent_role = db.session.scalar(select(Role).where(Role.nom == ROLE_AGENT))
    users = db.session.scalars(select(User).where(User.role_id == agent_role.id).order_by(User.nom.asc())).all() if agent_role else []
    return render_template("admin/agents.html", users=users)

@admin_bp.route("/agents/create", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def create_agent():
    form = AgentForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if db.session.scalar(select(User).where(User.email == email)):
            flash("Cet email existe déjà.", "warning")
            return render_template("admin/agent_form.html", form=form)
        agent_role = db.session.scalar(select(Role).where(Role.nom == ROLE_AGENT))
        agent = User(
            nom=form.nom.data,
            prenom=form.prenom.data,
            email=email,
            role=agent_role,
            role_locked=True,
            statut_compte=STATUT_COMPTE_VALIDE,
            date_validation=datetime.now(timezone.utc),
            valide_par_id=current_user.id,
        )
        agent.set_password(form.password.data)
        db.session.add(agent)
        db.session.flush()
        log_action("Création agent", entite="users", entite_id=agent.id)
        db.session.commit()
        flash("Agent créé. Son rôle est verrouillé.", "success")
        return redirect(url_for("admin.agents"))
    return render_template("admin/agent_form.html", form=form)

@admin_bp.route("/journaux")
@role_required(ROLE_ADMIN)
def journaux():
    logs = db.session.scalars(select(HistoriqueAction).order_by(HistoriqueAction.date_action.desc()).limit(200)).all()
    return render_template("admin/journaux.html", logs=logs)
