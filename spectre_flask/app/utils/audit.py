from flask_login import current_user
from . import workflow
from app.extensions import db
from app.models import HistoriqueAction


def log_action(action, demande=None, entite=None, entite_id=None, ancien_statut=None,
               nouveau_statut=None, commentaire=None, utilisateur=None):
    user = utilisateur
    if user is None and hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
        user = current_user

    historique = HistoriqueAction(
        utilisateur_id=user.id if user else None,
        demande_id=demande.id if demande else None,
        action=action,
        entite=entite,
        entite_id=entite_id,
        ancien_statut=ancien_statut,
        nouveau_statut=nouveau_statut,
        commentaire=commentaire,
    )
    db.session.add(historique)
    return historique
