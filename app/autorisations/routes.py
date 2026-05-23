from flask import Blueprint, render_template
from sqlalchemy import select
from flask_login import current_user

from app.models import Autorisation, DemandeAutorisation
from app.extensions import db
from app.utils.constants import ROLE_ADMIN, ROLE_AGENT, ROLE_UTILISATEUR
from app.utils.decorators import role_required

autorisations_bp = Blueprint("autorisations", __name__, url_prefix="/autorisations")

@autorisations_bp.route("/")
@role_required(ROLE_ADMIN, ROLE_AGENT, ROLE_UTILISATEUR)
def index():
    query = select(Autorisation).order_by(Autorisation.date_creation.desc())
    if current_user.has_role(ROLE_UTILISATEUR):
        query = query.join(Autorisation.demande).where(DemandeAutorisation.utilisateur_id == current_user.id)
    autorisations = db.session.scalars(query).all()
    return render_template("autorisations/index.html", autorisations=autorisations)
