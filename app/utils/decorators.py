from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user, login_required
from .constants import ROLE_ADMIN, ROLE_AGENT, STATUT_COMPTE_VALIDE

def role_required(*role_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                internal_roles = {ROLE_ADMIN, ROLE_AGENT}
                login_endpoint = (
                    "auth.login_interne"
                    if internal_roles.intersection(role_names)
                    else "auth.login_utilisateur"
                )
                return redirect(url_for(login_endpoint))
            if not current_user.has_role(*role_names):
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator

def validated_account_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.statut_compte != STATUT_COMPTE_VALIDE:
            flash("Votre compte n'est pas encore validé par l'administrateur.", "warning")
            return redirect(url_for("auth.login_utilisateur"))
        return view_func(*args, **kwargs)
    return wrapped
