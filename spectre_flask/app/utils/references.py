from datetime import datetime

from app.models import DemandeAutorisation, Autorisation


def generate_demande_reference():
    year = datetime.utcnow().year
    count = DemandeAutorisation.query.filter(
        DemandeAutorisation.reference.like(f"DAF-{year}-%")
    ).count() + 1
    return f"DAF-{year}-{count:04d}"


def generate_autorisation_number():
    year = datetime.utcnow().year
    count = Autorisation.query.filter(
        Autorisation.numero_autorisation.like(f"AUT-{year}-%")
    ).count() + 1
    return f"AUT-{year}-{count:04d}"
