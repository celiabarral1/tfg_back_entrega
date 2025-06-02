import tempfile
import pytest
import json
import os
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from app.module_analysis.analysis_controller import analysis_bp
from app.auth.auth_controller import auth_bp


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
    assert data["msg"] == "Credenciales inválidas"