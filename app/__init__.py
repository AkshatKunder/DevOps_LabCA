"""Flask application for the AI-Powered Online Quiz."""

import os

from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager

from app.database import init_db

load_dotenv()

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(_PROJECT_ROOT, "templates"),
    static_folder=os.path.join(_PROJECT_ROOT, "static"),
)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "dev-secret-key-local-use-only",
)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


def register_routes():
    """Register application routes."""
    from app.routes import main as routes_blueprint
    from app.auth import auth as auth_blueprint

    app.register_blueprint(routes_blueprint)
    app.register_blueprint(auth_blueprint)


register_routes()
init_db()
