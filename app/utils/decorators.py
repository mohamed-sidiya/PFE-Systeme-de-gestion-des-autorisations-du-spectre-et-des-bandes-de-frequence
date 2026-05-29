from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user, login_required
from .constants import ROLE_ADMIN, ROLE_AGENT, STATUT_COMPTE_VALIDE

def role_required(*role_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                if ROLE_ADMIN in role_names and ROLE_AGENT not in role_names:
                    login_endpoint = "auth.login_admin"
                elif ROLE_AGENT in role_names and ROLE_ADMIN not in role_names:
                    login_endpoint = "auth.login_agent"
                elif ROLE_ADMIN in role_names or ROLE_AGENT in role_names:
                    login_endpoint = "auth.login_admin"
                else:
                    login_endpoint = "auth.login_utilisateur"
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
