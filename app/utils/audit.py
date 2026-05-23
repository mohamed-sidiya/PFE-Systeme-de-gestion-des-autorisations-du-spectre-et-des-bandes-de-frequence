from flask_login import current_user
from app.extensions import db
from app.models import HistoriqueAction

def log_action(action, demande=None, ancien_statut=None, nouveau_statut=None, commentaire=None, entite=None, entite_id=None):
    user_id = current_user.id if getattr(current_user, "is_authenticated", False) else None
    item = HistoriqueAction(
        utilisateur_id=user_id,
        demande_id=demande.id if demande else None,
        action=action,
        entite=entite,
        entite_id=entite_id,
        ancien_statut=ancien_statut,
        nouveau_statut=nouveau_statut,
        commentaire=commentaire,
    )
    db.session.add(item)
    return item
