from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import select

from app.extensions import db
from app.models import User, Role, ProfilUtilisateur
from app.utils.constants import (
    ROLE_ADMIN,
    ROLE_AGENT,
    ROLE_UTILISATEUR,
    STATUT_COMPTE_ATTENTE,
    STATUT_COMPTE_VALIDE,
)
from .forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__)


def _redirect_authenticated_user():
    if current_user.has_role(ROLE_ADMIN):
        return redirect(url_for("admin.comptes"))
    if current_user.has_role(ROLE_AGENT):
        return redirect(url_for("agent.dashboard"))
    if current_user.has_role(ROLE_UTILISATEUR):
        return redirect(url_for("utilisateur.dashboard"))
    return redirect(url_for("auth.login_utilisateur"))


def _authenticate(form, allowed_roles, template_name, portal_name):
    user = db.session.scalar(select(User).where(User.email == form.email.data.lower().strip()))
    if not user or not user.check_password(form.password.data):
        flash("Email ou mot de passe incorrect.", "danger")
        return render_template(template_name, form=form, portal_name=portal_name)

    if not any(user.has_role(role) for role in allowed_roles):
        flash(f"Ce compte n'est pas autorise a utiliser l'espace {portal_name}.", "warning")
        return render_template(template_name, form=form, portal_name=portal_name)

    if user.statut_compte != STATUT_COMPTE_VALIDE:
        flash("Votre compte n'est pas encore valide ou il est suspendu.", "warning")
        return render_template(template_name, form=form, portal_name=portal_name)

    user.derniere_connexion = datetime.utcnow()
    db.session.commit()
    login_user(user, remember=form.remember.data)
    return _redirect_authenticated_user()


@auth_bp.route("/connexion")
def connexion():
    return redirect(url_for("auth.login_utilisateur"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_authenticated_user()
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        existing = db.session.scalar(select(User).where(User.email == email))
        if existing:
            flash("Cet email est deja utilise.", "warning")
            return render_template("auth/register.html", form=form)

        role = db.session.scalar(select(Role).where(Role.nom == ROLE_UTILISATEUR))
        user = User(
            nom=form.nom.data,
            prenom=form.prenom.data,
            email=email,
            role=role,
            role_locked=True,
            statut_compte=STATUT_COMPTE_ATTENTE,
        )
        user.set_password(form.password.data)
        user.profil = ProfilUtilisateur(
            type_utilisateur=form.type_utilisateur.data,
            raison_sociale=form.raison_sociale.data,
            identifiant=form.identifiant.data,
            telephone=form.telephone.data,
            adresse=form.adresse.data,
            secteur_activite=form.secteur_activite.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("Compte cree. Vous pourrez vous connecter apres validation par l'administrateur.", "success")
        return redirect(url_for("auth.login_utilisateur"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return redirect(url_for("auth.login_utilisateur"))


@auth_bp.route("/connexion-utilisateur", methods=["GET", "POST"])
def login_utilisateur():
    if current_user.is_authenticated:
        return _redirect_authenticated_user()
    form = LoginForm()
    if form.validate_on_submit():
        return _authenticate(
            form=form,
            allowed_roles=(ROLE_UTILISATEUR,),
            template_name="auth/login_utilisateur.html",
            portal_name="utilisateur",
        )
    return render_template("auth/login_utilisateur.html", form=form, portal_name="utilisateur")


@auth_bp.route("/connexion-interne", methods=["GET", "POST"])
def login_interne():
    return redirect(url_for("auth.login_admin"))


@auth_bp.route("/connexion-admin", methods=["GET", "POST"])
def login_admin():
    if current_user.is_authenticated:
        return _redirect_authenticated_user()
    form = LoginForm()
    if form.validate_on_submit():
        return _authenticate(
            form=form,
            allowed_roles=(ROLE_ADMIN,),
            template_name="auth/login_interne.html",
            portal_name="administration",
        )
    return render_template("auth/login_interne.html", form=form, portal_name="administration")


@auth_bp.route("/connexion-agent", methods=["GET", "POST"])
def login_agent():
    if current_user.is_authenticated:
        return _redirect_authenticated_user()
    form = LoginForm()
    if form.validate_on_submit():
        return _authenticate(
            form=form,
            allowed_roles=(ROLE_AGENT,),
            template_name="auth/login_interne.html",
            portal_name="agent",
        )
    return render_template("auth/login_interne.html", form=form, portal_name="agent")


@auth_bp.route("/logout")
def logout():
    return redirect(url_for("auth.logout_utilisateur"))


@auth_bp.route("/deconnexion-utilisateur")
def logout_utilisateur():
    logout_user()
    flash("Vous etes deconnecte.", "info")
    return redirect(url_for("auth.login_utilisateur"))


@auth_bp.route("/deconnexion-admin")
def logout_admin():
    logout_user()
    flash("Vous etes deconnecte.", "info")
    return redirect(url_for("auth.login_admin"))


@auth_bp.route("/deconnexion-agent")
def logout_agent():
    logout_user()
    flash("Vous etes deconnecte.", "info")
    return redirect(url_for("auth.login_agent"))
