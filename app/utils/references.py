from datetime import datetime
from app.extensions import db
from app.models import DemandeAutorisation, Autorisation, Facture

def generate_demande_reference():
    year = datetime.utcnow().year
    count = db.session.query(DemandeAutorisation).filter(
        DemandeAutorisation.reference.like(f"DEM-{year}-%")
    ).count() + 1
    return f"DEM-{year}-{count:04d}"

def generate_autorisation_number():
    year = datetime.utcnow().year
    count = db.session.query(Autorisation).filter(
        Autorisation.numero_autorisation.like(f"AUT-{year}-%")
    ).count() + 1
    return f"AUT-{year}-{count:04d}"

def generate_facture_number():
    year = datetime.utcnow().year
    count = db.session.query(Facture).filter(
        Facture.numero_facture.like(f"FAC-{year}-%")
    ).count() + 1
    return f"FAC-{year}-{count:04d}"
