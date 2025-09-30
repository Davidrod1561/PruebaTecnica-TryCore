"""Manejo de errores."""
from flask import Flask, jsonify


def register_error_handlers(app: Flask) -> None:
    """Registra los manejadores de error."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Maneja errores de JSON inválido."""
        return jsonify({"error": "JSON inválido"}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Maneja errores de recurso no encontrado."""
        return jsonify({"error": "Recurso no encontrado"}), 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Maneja errores de validaciones faltantes."""
        return jsonify({"error": "Validaciones faltantes"}), 422
