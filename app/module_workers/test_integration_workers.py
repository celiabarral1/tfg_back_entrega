import pytest
from flask import Flask
from app.module_workers.worker import RolModel
from app.module_workers.workers_processor import WorkersProcessor
from app.persistance.worker_persistance import WorkersDataCSV
from app.module_workers.worker_controller import workers_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(workers_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_roles(client):
    response = client.get('/getRols')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_ids_no_rol(client):
    response = client.get('/workers/getIds')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_register_worker_success(client):
    data = {'id': '104', 'rol': 'operario', 'registrationDate': '2025-02-03T00:00:00.000Z'}
    response = client.post('/workers/register', json=data)
    assert response.status_code == 201
    assert response.get_json() == {"message": "Trabajador registrado"}

def test_register_worker_not_found(client):
    data = {"id": -10, "rol": "User", "registrationDate": "2025-02-03"}
    response = client.post('/workers/register', json=data)
    assert response.status_code == 400
    assert response.get_json() == {"message": "No hay trabajadores con ese id"}