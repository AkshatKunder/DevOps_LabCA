"""Flask application for the AI-Powered Online Quiz."""
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env (e.g. GEMINI_API_KEY)
load_dotenv()

app = Flask(__name__)

# Secret key required for Flask sessions (keeps quiz data server-side).
app.secret_key = "dev-secret-key-local-use-only"


def register_routes():
    """Register all application routes."""
    from app.routes import main as routes_blueprint

    app.register_blueprint(routes_blueprint)


register_routes()