"""Modelos de datos."""
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TransactionStatus(Enum):
    """Estados de transacción."""
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    PROCESADO = "PROCESADO"
    ERROR = "ERROR"


class Company(Base):
    """Modelo de empresa."""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True)
    nit = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relación con transacciones
    transactions = relationship("Transaction", back_populates="company")


class Transaction(Base):
    """Modelo de transacción."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    nit = Column(String, index=True)
    status = Column(String)  # Enum como string
    payload_in = Column(Text)
    result_payload = Column(Text)
    error_code = Column(String, nullable=True)
    error_msg = Column(String, nullable=True)
    runner_id = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relación con empresa
    company = relationship("Company", back_populates="transactions")


class AuditLog(Base):
    """Modelo de log de auditoría."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    entity = Column(String)
    entity_id = Column(Integer)
    action = Column(String)
    detail = Column(Text)
    created_at = Column(DateTime, default=func.now())
