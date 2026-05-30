from functools import wraps

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from .constants import ROLE_ADMIN, ROLE_AGENT, ROLE_UTILISATEUR, STATUT_COMPTE_VALIDE


def _login_endpoint_for_roles(role_names):
    portal = request.args.get("portal")
    if portal == "agent" and ROLE_AGENT in role_names:
        return "auth.login_agent"
    if portal == "admin" and ROLE_ADMIN in role_names:
        return "auth.login_admin"
    if portal == "utilisateur" and ROLE_UTILISATEUR in role_names:
        return "auth.login_utilisateur"

    if ROLE_ADMIN in role_names and ROLE_AGENT not in role_names:
        return "auth.login_admin"
    if ROLE_AGENT in role_names and ROLE_ADMIN not in role_names:
        return "auth.login_agent"
    if ROLE_ADMIN in role_names or ROLE_AGENT in role_names:
        return "auth.login_admin"
    return "auth.login_utilisateur"


def role_required(*role_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for(_login_endpoint_for_roles(role_names)))
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
            flash("Votre compte n'est pas encore valide par l'administrateur.", "warning")
            return redirect(url_for("auth.login_utilisateur"))
        return view_func(*args, **kwargs)

    return wrapped
