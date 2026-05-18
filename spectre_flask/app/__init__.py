import os
from flask import Flask

from .config import Config
from .extensions import db, migrate, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "warning"

    # Import des modèles pour que Flask-Migrate les détecte.
    from . import models  # noqa: F401

    from .auth.routes import auth_bp
    from .dashboard.routes import dashboard_bp
    from .admin.routes import admin_bp
    from .bandes.routes import bandes_bp
    from .demandes.routes import demandes_bp
    from .autorisations.routes import autorisations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bandes_bp)
    app.register_blueprint(demandes_bp)
    app.register_blueprint(autorisations_bp)

    from .commands import seed_command
    app.cli.add_command(seed_command)

    return app
