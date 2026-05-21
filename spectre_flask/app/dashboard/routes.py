from flask import Blueprint, render_template
from flask_login import login_required

from app.models import DemandeAutorisation, Autorisation, Demandeur, BandeFrequence


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    stats = {
        "demandeurs": Demandeur.query.count(),
        "bandes": BandeFrequence.query.count(),
        "demandes": DemandeAutorisation.query.count(),
        "demandes_pretes": DemandeAutorisation.query.filter_by(statut="prete_decision").count(),
        "demandes_validees": DemandeAutorisation.query.filter(
            DemandeAutorisation.statut.in_(("validee", "autorisation_generee"))
        ).count(),
        "demandes_rejetees": DemandeAutorisation.query.filter_by(statut="rejetee").count(),
        "autorisations": Autorisation.query.count(),
    }
    recentes = DemandeAutorisation.query.order_by(DemandeAutorisation.date_creation.desc()).limit(5).all()
    return render_template("dashboard/index.html", stats=stats, recentes=recentes)
