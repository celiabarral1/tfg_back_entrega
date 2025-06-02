"""
test_auth.py

Tests unitarios para validar el sistema de autenticación local mediante bcrypt.
"""

from app.auth.auth_controller import users, bcrypt
from flask_jwt_extended import create_access_token

def test_login_correct():
    """
    Test que verifica la autenticación de un usuario con credenciales válidas.

    Resultado esperado:
       La autenticación se completa.
    """
    id = "101"
    password = "operator1"

    hashed_password = users[id]["password"]
    assert bcrypt.check_password_hash(hashed_password, password)  

def test_login_incorrect():
    """
    Test que verifica el fallo de autenticación con una contraseña incorrecta.

    Resultado esperado:
        La autenticación falla.
    """
    id = "101"
    password = "error"

    hashed_password = users[id]["password"]
    assert not bcrypt.check_password_hash(hashed_password, password)  



