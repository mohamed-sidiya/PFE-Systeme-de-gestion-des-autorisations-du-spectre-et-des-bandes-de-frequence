from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user

from app.extensions import db
from app.models import DemandeAutorisation, User
from app.utils.constants import ROLE_ADMIN, ROLE_AGENT, ROLE_UTILISATEUR

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def index():
    if current_user.has_role(ROLE_UTILISATEUR):
        return redirect(url_for("utilisateur.dashboard"))
    if current_user.has_role(ROLE_AGENT):
        return redirect(url_for("agent.dashboard"))
    if current_user.has_role(ROLE_ADMIN):
        stats = {
            "utilisateurs": db.session.query(User).count(),
            "demandes": db.session.query(DemandeAutorisation).count(),
            "en_attente": db.session.query(User).filter_by(statut_compte="en_attente").count(),
            "soumises": db.session.query(DemandeAutorisation).filter(DemandeAutorisation.statut.in_(["soumise", "completee"])).count(),
        }
        return render_template("dashboard/admin.html", stats=stats)
    return render_template("dashboard/index.html")
