from functools import wraps
from flask import abort
from flask_login import current_user, login_required


PERMISSIONS_INITIALES = [
    ("gerer_utilisateurs", "Gérer les utilisateurs"),
    ("gerer_roles", "Gérer les rôles"),
    ("gerer_bandes", "Gérer les bandes de fréquence"),
    ("consulter_journaux", "Consulter les journaux d'activité"),
    ("gerer_demandeurs", "Enregistrer les demandeurs"),
    ("creer_demande", "Créer une demande"),
    ("modifier_demande", "Modifier une demande"),
    ("consulter_demande", "Suivre et consulter les demandes"),
    ("ajouter_piece", "Ajouter des pièces jointes"),
    ("ajouter_observation", "Ajouter des observations"),
    ("verifier_dossier", "Vérifier le dossier"),
    ("valider_demande", "Valider une demande"),
    ("rejeter_demande", "Rejeter une demande"),
    ("generer_autorisation", "Générer une autorisation"),
    ("consulter_statistiques", "Consulter les statistiques"),
]

PERMISSION_LABELS = dict(PERMISSIONS_INITIALES)

ROLES_INITIAUX = {
    "Administrateur": [code for code, _description in PERMISSIONS_INITIALES],
    "Agent": [
        "gerer_demandeurs", "creer_demande", "modifier_demande", "consulter_demande",
        "ajouter_piece", "ajouter_observation", "verifier_dossier", "gerer_bandes",
    ],
    "Responsable": [
        "consulter_demande", "ajouter_observation", "valider_demande", "rejeter_demande",
        "generer_autorisation", "consulter_statistiques",
    ],
}


def permission_label(permission_code):
    return PERMISSION_LABELS.get(permission_code, permission_code.replace("_", " ").capitalize())


def permission_required(permission_code):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(*args, **kwargs):
            if not current_user.can(permission_code):
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator


def any_permission_required(*permission_codes):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(*args, **kwargs):
            if not any(current_user.can(code) for code in permission_codes):
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator
