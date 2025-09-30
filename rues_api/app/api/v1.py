"""API versión 1."""
from flask import Blueprint, request, jsonify

from app.services.transactions_service import TransactionsService
from app.core.auth import require_api_key, issue_api_key
from app.core.config import Config

api_v1 = Blueprint("api_v1", __name__)
transactions_service = TransactionsService()


@api_v1.route("/process-data", methods=["POST"])
@require_api_key
def process_data():
    """Procesa datos y crea una transacción pendiente."""
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400
    
    payload = request.get_json()
    if not payload or "nit" not in payload:
        return jsonify({"error": "Campo 'nit' es requerido"}), 422
    
    # Validación más robusta del NIT
    nit = payload.get("nit")
    if not isinstance(nit, str) or len(nit.strip()) < 5:
        return jsonify({"error": "NIT debe ser string de al menos 5 caracteres"}), 422
    
    idempotency_key = request.headers.get("Idempotency-Key")
    
    transaction = transactions_service.create_transaction(payload, idempotency_key)
    return jsonify(transaction), 201


@api_v1.route("/update-status", methods=["POST"])
@require_api_key
def update_status():
    """Actualiza el estado de una transacción."""
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos JSON requeridos"}), 422
    
    # Validar que tenga id o nit
    if "id" not in data and "nit" not in data:
        return jsonify({"error": "Campo 'id' o 'nit' es requerido"}), 422
    
    # Validación más robusta de id y nit
    if "id" in data and (not isinstance(data["id"], int) or data["id"] <= 0):
        return jsonify({"error": "Campo 'id' debe ser entero positivo"}), 422
    
    if "nit" in data:
        nit = data["nit"]
        if not isinstance(nit, str) or len(nit.strip()) < 5:
            return jsonify({"error": "NIT debe ser string de al menos 5 caracteres"}), 422
    
    # Validar status
    if "status" not in data:
        return jsonify({"error": "Campo 'status' es requerido"}), 422
    
    valid_statuses = {"PENDIENTE", "PROCESADO", "ERROR"}
    if data["status"] not in valid_statuses:
        return jsonify({"error": f"Status debe ser uno de: {', '.join(valid_statuses)}"}), 422
    
    selector = {}
    if "id" in data:
        selector["id"] = data["id"]
    if "nit" in data:
        selector["nit"] = data["nit"]
    
    update_data = {"status": data["status"]}
    if "error_code" in data:
        update_data["error_code"] = data["error_code"]
    if "error_msg" in data:
        update_data["error_msg"] = data["error_msg"]
    if "result_payload" in data:
        update_data["result_payload"] = data["result_payload"]
    
    try:
        transaction = transactions_service.update_status(selector, update_data)
        return jsonify(transaction), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@api_v1.route("/auth/login", methods=["POST"])
def login():
    """Endpoint de autenticación."""
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos JSON requeridos"}), 400
    
    username = data.get("username")
    password = data.get("password")
    
    if username == Config.ADMIN_USER and password == Config.ADMIN_PASS:
        token_data = issue_api_key(username)
        return jsonify(token_data), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@api_v1.route("/health", methods=["GET"])
def health():
    """Endpoint de salud."""
    return jsonify({"status": "ok"}), 200


@api_v1.route("/next", methods=["GET"])
@require_api_key
def next_transaction():
    """Obtiene la siguiente transacción pendiente y la marca como procesando."""
    transaction = transactions_service.fetch_next_pending()
    
    if transaction is None:
        return "", 204
    
    # Marcar como PROCESANDO
    try:
        updated_transaction = transactions_service.update_status(
            {"id": transaction["id"]}, 
            {"status": "PROCESANDO"}
        )
        return jsonify(updated_transaction), 200
    except ValueError:
        return "", 204
