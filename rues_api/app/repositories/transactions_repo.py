"""Repositorio de transacciones."""
import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import Transaction, TransactionStatus


def create_transaction(session: Session, payload: dict, idempotency_key: Optional[str] = None) -> Transaction:
    """Crea una nueva transacción."""
    transaction = Transaction(
        nit=payload.get("nit"),
        status=TransactionStatus.PENDIENTE.value,
        payload_in=json.dumps(payload),
        idempotency_key=idempotency_key
    )
    session.add(transaction)
    session.flush()
    return transaction


def update_status(
    session: Session,
    *,
    id: Optional[int] = None,
    nit: Optional[str] = None,
    status: str,
    error_code: Optional[str] = None,
    error_msg: Optional[str] = None,
    result_payload: Optional[dict] = None
) -> Transaction:
    """Actualiza el estado de una transacción."""
    query = session.query(Transaction)
    
    if id is not None:
        query = query.filter(Transaction.id == id)
    elif nit is not None:
        query = query.filter(Transaction.nit == nit)
    else:
        raise ValueError("Debe proporcionar id o nit")
    
    transaction = query.first()
    if transaction is None:
        raise ValueError("Transacción no encontrada")
    
    transaction.status = status
    if error_code is not None:
        transaction.error_code = error_code
    if error_msg is not None:
        transaction.error_msg = error_msg
    if result_payload is not None:
        transaction.result_payload = json.dumps(result_payload)
    
    session.flush()
    return transaction


def fetch_next_pending(session: Session) -> Transaction | None:
    """Obtiene la siguiente transacción pendiente."""
    return session.query(Transaction).filter(
        Transaction.status == TransactionStatus.PENDIENTE.value
    ).first()
