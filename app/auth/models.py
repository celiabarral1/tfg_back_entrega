# app/auth/models.py

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Simulación de base de datos para autenticación
users = {
    "101": {
        "password": bcrypt.generate_password_hash("password1").decode('utf-8'),
        "role": "operator"
    },
    "202": {
        "password": bcrypt.generate_password_hash("inmerbot").decode('utf-8'),
        "role": "psychologist"
    },
    "admin": {
        "password": bcrypt.generate_password_hash("admin").decode('utf-8'),
        "role": "admin"
    }
}
