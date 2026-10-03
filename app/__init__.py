"""Flask application for the AI-Powered Online Quiz."""
import os

from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env (e.g. GEMINI_API_KEY)
load_dotenv()

# templates/ and static/ live at the project root, one level above this
# package, so they must be pointed to explicitly (Flask's default looks
# for them inside the app/ package directory).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    template_folder=os.path.join(_PROJECT_ROOT, "templates"),
    static_folder=os.path.join(_PROJECT_ROOT, "static"),
)

# Secret key required for Flask sessions (keeps quiz data server-side).
# Falls back to a dev-only default so local runs still work without a .env.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-local-use-only")


def register_routes():
    """Register all application routes."""
    from app.routes import main as routes_blueprint

    app.register_blueprint(routes_blueprint)


register_routes()