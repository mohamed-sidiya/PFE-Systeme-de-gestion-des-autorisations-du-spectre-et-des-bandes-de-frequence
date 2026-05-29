from flask import Flask, redirect, url_for
from .config import Config
from .extensions import db, migrate, login_manager, csrf
from .commands import seed_command, seed_bandes_command

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login_utilisateur"
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."

    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .utilisateur.routes import utilisateur_bp
    from .agent.routes import agent_bp
    from .bandes.routes import bandes_bp
    from .autorisations.routes import autorisations_bp
    from .dashboard.routes import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(utilisateur_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(bandes_bp)
    app.register_blueprint(autorisations_bp)
    app.register_blueprint(dashboard_bp)

    app.cli.add_command(seed_command)
    app.cli.add_command(seed_bandes_command)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login_utilisateur"))

    return app
