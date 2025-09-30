"""Repositorio de empresas."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import Company


def get_or_create_company(session: Session, nit: str, name: Optional[str] = None) -> Company:
    """Obtiene o crea una empresa por NIT."""
    company = session.query(Company).filter(Company.nit == nit).first()
    
    if company is None:
        company = Company(nit=nit, name=name)
        session.add(company)
        session.flush()
    
    return company
