"""Autenticación con API Keys temporales."""
import uuid
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict

from flask import request, jsonify

from app.core.config import Config

# Almacén en memoria para API Keys temporales
_ISSUED_KEYS: Dict[str, datetime] = {}


def issue_api_key(username: str) -> dict:
    """Genera una API Key temporal."""
    api_key = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(minutes=Config.API_KEY_TTL_MINUTES)
    _ISSUED_KEYS[api_key] = expires_at
    
    return {
        "api_key": api_key,
        "expires_in_minutes": Config.API_KEY_TTL_MINUTES
    }


def is_valid_api_key(key: str) -> bool:
    """Valida si una API Key es válida."""
    # Verificar si es la API Key estática
    if key == Config.API_KEY:
        return True
    
    # Verificar si es una API Key temporal
    if key in _ISSUED_KEYS:
        expires_at = _ISSUED_KEYS[key]
        if datetime.now() < expires_at:
            return True
        else:
            # Eliminar clave expirada
            del _ISSUED_KEYS[key]
            return False
    
    return False


def require_api_key(f):
    """Decorador que requiere API Key válida en header X-API-Key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or not is_valid_api_key(api_key):
            return jsonify({"error": "Unauthorized"}), 401
        
        return f(*args, **kwargs)
    return decorated_function
