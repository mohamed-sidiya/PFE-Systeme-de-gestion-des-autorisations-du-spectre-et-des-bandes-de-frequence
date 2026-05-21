from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import select

from app.extensions import db
from app.models import User
from .forms import LoginForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = db.session.execute(select(User).filter_by(email=email)).scalar_one_or_none()
        if user and user.check_password(form.password.data) and user.actif:
            user.derniere_connexion = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=form.remember.data)
            flash("Connexion réussie.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Identifiants incorrects ou compte désactivé.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Déconnexion effectuée.", "info")
    return redirect(url_for("auth.login"))
