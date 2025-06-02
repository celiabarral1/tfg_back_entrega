import tempfile
import pytest
import json
import os
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from app.module_analysis.analysis_controller import analysis_bp
from app.auth.auth_controller import auth_bp

CSV_TEST_PATH = "resources/test_data.csv"

@pytest.fixture
def app():
    """ Configura una aplicación Flask de prueba """
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test_key"  # Clave secreta para JWT en modo test
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(analysis_bp, url_prefix="/analysis")
    
    jwt = JWTManager(app)

    return app

@pytest.fixture
def client(app):
    """ Proporciona un cliente de prueba para realizar peticiones HTTP """
    return app.test_client()

def test_login_success(client):
    """ Verifica que un usuario válido pueda iniciar sesión """
    response = client.post("/auth/login", json={"username": "101", "password": "operator1"})
    data = response.get_json()
    
    assert response.status_code == 200
    assert "access_token" in data

def test_login_failure(client):
    """ Verifica que un usuario con credenciales inválidas no pueda iniciar sesión """
    response = client.post("/auth/login", json={"username": "101", "password": "wrongpassword"})
    data = response.get_json()

    assert response.status_code == 401

def test_classify_users(client, monkeypatch):
    """ Prueba la clasificación de usuarios desde un archivo CSV simulado """

    # Simulación de datos CSV en memoria
    csv_data = """user_id;Predicted_Condition
    1;no_disorder
    2;depression
    3;anxiety
    4;no_disorder
    5;depression"""

    # Crear un archivo CSV temporal
    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', encoding='utf-8') as temp_file:
        temp_file.write(csv_data)
        temp_file_path = temp_file.name

    # Simulamos el CSV path en el módulo
    monkeypatch.setattr("app.module_analysis.analysis_controller.csv_path", temp_file_path)

    # Realizamos la petición
    response = client.get("/analysis/classify")
    data = response.get_json()

    assert response.status_code == 200
    assert set(data.keys()) == {"no_disorder", "depression", "anxiety"}
    assert data["no_disorder"] == [1, 4]
    assert data["depression"] == [2, 5]
    assert data["anxiety"] == [3]

    # Eliminar el archivo temporal
    os.remove(temp_file_path)