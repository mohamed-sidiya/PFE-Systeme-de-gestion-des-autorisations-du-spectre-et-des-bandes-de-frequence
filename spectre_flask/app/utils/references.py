from datetime import datetime

from sqlalchemy import func, select

from app.extensions import db
from app.models import DemandeAutorisation, Autorisation


def generate_demande_reference():
    year = datetime.utcnow().year
    count = db.session.scalar(
        select(func.count())
        .select_from(DemandeAutorisation)
        .where(DemandeAutorisation.reference.like(f"DAF-{year}-%"))
    ) or 0
    return f"DAF-{year}-{count + 1:04d}"


def generate_autorisation_number():
    year = datetime.utcnow().year
    count = db.session.scalar(
        select(func.count())
        .select_from(Autorisation)
        .where(Autorisation.numero_autorisation.like(f"AUT-{year}-%"))
    ) or 0
    return f"AUT-{year}-{count + 1:04d}"
