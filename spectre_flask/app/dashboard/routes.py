from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func, select

from app.extensions import db
from app.models import DemandeAutorisation, Autorisation, Demandeur, BandeFrequence


dashboard_bp = Blueprint("dashboard", __name__)


def count_rows(model, *criteria):
    stmt = select(func.count()).select_from(model)
    if criteria:
        stmt = stmt.where(*criteria)
    return db.session.scalar(stmt) or 0


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    stats = {
        "demandeurs": count_rows(Demandeur),
        "bandes": count_rows(BandeFrequence),
        "demandes": count_rows(DemandeAutorisation),
        "demandes_pretes": count_rows(DemandeAutorisation, DemandeAutorisation.statut == "prete_decision"),
        "demandes_validees": count_rows(
            DemandeAutorisation,
            DemandeAutorisation.statut.in_(("validee", "autorisation_generee")),
        ),
        "demandes_rejetees": count_rows(DemandeAutorisation, DemandeAutorisation.statut == "rejetee"),
        "autorisations": count_rows(Autorisation),
    }
    recentes = db.session.scalars(
        select(DemandeAutorisation).order_by(DemandeAutorisation.date_creation.desc()).limit(5)
    ).all()
    return render_template("dashboard/index.html", stats=stats, recentes=recentes)
