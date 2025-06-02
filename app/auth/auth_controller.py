"""
auth_controller.py

Módulo de autenticación para el sistema Flask.
Proporciona el endpoint de login y una base de datos simulada con roles.

Blueprints:
    auth_bp: Blueprint principal del módulo de autenticación.

"""

from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# Simulación de base la datos para autenticación
# ROLES: Operador, admin, psicólogo
users = {
    "101": {
        "password": bcrypt.generate_password_hash("operator1").decode('utf-8'),
        "role": "operator"
    },
    "202": {
        "password": bcrypt.generate_password_hash("password2").decode('utf-8'),
        "role": "psychologist"
    },
    "admin": {
        "password": bcrypt.generate_password_hash("admin").decode('utf-8'),
        "role": "admin"
    }
}

# Endpoint para iniciar sesión.
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Autenticación de usuario mediante nombre de usuario y contraseña.

    Devuelve:
        JSON con token de acceso JWT si las credenciales son correctas.
        401 en caso de error de autenticación.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users and bcrypt.check_password_hash(users[username]['password'], password):
        access_token = create_access_token(identity={"username": username, "role": users[username]['role']}) # Generación del token de sesión
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Credenciales inválidas"}), 401