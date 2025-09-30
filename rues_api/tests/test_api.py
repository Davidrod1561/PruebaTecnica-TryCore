"""Tests de la API."""
import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from app.models.models import Base
from app.db.session import SessionLocal
from app.services.transactions_service import TransactionsService


@pytest.fixture
def app():
    """Fixture de la aplicación Flask en modo testing."""
    app = create_app()
    app.config['TESTING'] = True
    
    # Configurar SQLite en memoria para tests
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    
    # Reemplazar SessionLocal para usar la DB de test
    test_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Monkey patch para usar la sesión de test
    original_session = SessionLocal
    import app.db.session
    app.db.session.SessionLocal = test_session
    
    yield app
    
    # Restaurar sesión original
    app.db.session.SessionLocal = original_session


@pytest.fixture
def client(app):
    """Fixture del cliente de test."""
    return app.test_client()


def test_process_data_ok(client):
    """Test POST /api/v1/process-data con nit válido -> 201 con status=PENDIENTE."""
    response = client.post(
        '/api/v1/process-data',
        data=json.dumps({'nit': '123456789'}),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['nit'] == '123456789'
    assert data['status'] == 'PENDIENTE'
    assert 'id' in data


def test_process_data_422(client):
    """Test POST sin nit -> 422."""
    response = client.post(
        '/api/v1/process-data',
        data=json.dumps({'other_field': 'value'}),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'error' in data


def test_update_status_ok(client):
    """Test crea transacción, luego POST /api/v1/update-status -> 200 y status actualizado."""
    # Crear transacción primero
    create_response = client.post(
        '/api/v1/process-data',
        data=json.dumps({'nit': '987654321'}),
        content_type='application/json'
    )
    assert create_response.status_code == 201
    transaction_data = create_response.get_json()
    transaction_id = transaction_data['id']
    
    # Actualizar status
    update_response = client.post(
        '/api/v1/update-status',
        data=json.dumps({
            'id': transaction_id,
            'status': 'PROCESADO'
        }),
        content_type='application/json'
    )
    
    assert update_response.status_code == 200
    updated_data = update_response.get_json()
    assert updated_data['status'] == 'PROCESADO'
    assert updated_data['id'] == transaction_id


def test_health_ok(client):
    """Test GET /api/v1/health -> 200."""
    response = client.get('/api/v1/health')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'status': 'ok'}


def test_login_ok(client):
    """Test POST /api/v1/auth/login con admin/admin -> 200 y campo api_key."""
    response = client.post(
        '/api/v1/auth/login',
        data=json.dumps({'username': 'admin', 'password': 'admin'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'api_key' in data
    assert 'expires_in_minutes' in data
    assert data['expires_in_minutes'] == 60


def test_login_invalid(client):
    """Test credenciales incorrectas -> 401."""
    response = client.post(
        '/api/v1/auth/login',
        data=json.dumps({'username': 'wrong', 'password': 'wrong'}),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == 'Invalid credentials'


def test_process_data_with_temp_key(client):
    """Test obtener api_key con login y luego llamar POST /api/v1/process-data."""
    # Obtener API key temporal
    login_response = client.post(
        '/api/v1/auth/login',
        data=json.dumps({'username': 'admin', 'password': 'admin'}),
        content_type='application/json'
    )
    assert login_response.status_code == 200
    login_data = login_response.get_json()
    api_key = login_data['api_key']
    
    # Usar API key temporal para crear transacción
    response = client.post(
        '/api/v1/process-data',
        data=json.dumps({'nit': '900123456'}),
        content_type='application/json',
        headers={'X-API-Key': api_key}
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['nit'] == '900123456'
    assert data['status'] == 'PENDIENTE'
