"""Aplicación Flask para la API de RUES."""
from flask import Flask

from app.api.v1 import api_v1
from app.core.errors import register_error_handlers


def create_app() -> Flask:
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    
    # Registrar blueprint
    app.register_blueprint(api_v1, url_prefix="/api/v1")
    
    # Registrar manejadores de error
    register_error_handlers(app)
    
    return app
