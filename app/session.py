from flask import request
from flask.sessions import SecureCookieSessionInterface


class PortalSessionInterface(SecureCookieSessionInterface):
    """Use one signed session cookie per testing portal.

    This lets a developer keep Utilisateur, Administrateur, and Agent sessions
    open in the same browser at the same time on localhost.
    """

    COOKIE_NAMES = {
        "admin": "spectre_admin_session",
        "agent": "spectre_agent_session",
        "utilisateur": "spectre_user_session",
    }

    def get_cookie_name(self, app):
        return self.COOKIE_NAMES.get(self._portal_from_request(), app.config["SESSION_COOKIE_NAME"])

    def _portal_from_request(self):
        path = request.path or ""
        endpoint = request.endpoint or ""

        if path.startswith("/admin") or path in {"/connexion-admin", "/deconnexion-admin"} or endpoint in {"auth.login_admin", "auth.logout_admin"}:
            return "admin"
        if path.startswith("/agent") or path in {"/connexion-agent", "/deconnexion-agent"} or endpoint in {"auth.login_agent", "auth.logout_agent"}:
            return "agent"
        if path.startswith("/utilisateur") or path in {"/connexion-utilisateur", "/deconnexion-utilisateur", "/register"} or endpoint in {"auth.login_utilisateur", "auth.logout_utilisateur", "auth.register"}:
            return "utilisateur"

        portal = request.args.get("portal")
        if portal in self.COOKIE_NAMES:
            return portal

        if path.startswith("/bandes"):
            return "admin"

        return "utilisateur"
