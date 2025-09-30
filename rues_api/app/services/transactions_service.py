"""Servicio de transacciones."""
from typing import Optional

from app.db.session import SessionLocal
from app.repositories import transactions_repo
from app.repositories.companies_repo import get_or_create_company


class TransactionsService:
    """Servicio para gestionar transacciones."""
    
    def create_transaction(self, payload: dict, idempotency_key: Optional[str] = None) -> dict:
        """Crea una nueva transacción."""
        session = SessionLocal()
        try:
            # Crear o obtener la empresa
            company = get_or_create_company(
                session, payload["nit"], payload.get("name")
            )
            
            # Crear la transacción
            transaction = transactions_repo.create_transaction(
                session, payload, idempotency_key
            )
            
            # Asignar company_id
            transaction.company_id = company.id
            session.commit()
            
            return {
                "id": transaction.id,
                "company_id": transaction.company_id,
                "nit": transaction.nit,
                "status": transaction.status,
                "payload_in": transaction.payload_in,
                "result_payload": transaction.result_payload,
                "error_code": transaction.error_code,
                "error_msg": transaction.error_msg,
                "runner_id": transaction.runner_id,
                "idempotency_key": transaction.idempotency_key,
                "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
            }
        finally:
            session.close()
    
    def update_status(self, selector: dict, data: dict) -> dict:
        """Actualiza el estado de una transacción."""
        session = SessionLocal()
        try:
            transaction = transactions_repo.update_status(
                session,
                id=selector.get("id"),
                nit=selector.get("nit"),
                status=data["status"],
                error_code=data.get("error_code"),
                error_msg=data.get("error_msg"),
                result_payload=data.get("result_payload")
            )
            session.commit()
            
            return {
                "id": transaction.id,
                "company_id": transaction.company_id,
                "nit": transaction.nit,
                "status": transaction.status,
                "payload_in": transaction.payload_in,
                "result_payload": transaction.result_payload,
                "error_code": transaction.error_code,
                "error_msg": transaction.error_msg,
                "runner_id": transaction.runner_id,
                "idempotency_key": transaction.idempotency_key,
                "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
            }
        finally:
            session.close()
    
    def fetch_next_pending(self) -> Optional[dict]:
        """Obtiene la siguiente transacción pendiente."""
        session = SessionLocal()
        try:
            transaction = transactions_repo.fetch_next_pending(session)
            
            if transaction is None:
                return None
            
            return {
                "id": transaction.id,
                "company_id": transaction.company_id,
                "nit": transaction.nit,
                "status": transaction.status,
                "payload_in": transaction.payload_in,
                "result_payload": transaction.result_payload,
                "error_code": transaction.error_code,
                "error_msg": transaction.error_msg,
                "runner_id": transaction.runner_id,
                "idempotency_key": transaction.idempotency_key,
                "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
            }
        finally:
            session.close()
