"""
auth_processor.py

Contiene decoradores para aplicar control de acceso basado en roles usando JWT.

"""

from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

# Función para delimitar acceso a funcionalidades por rol 
def role_required(role):
    """
    Decorador que restringe el acceso a una función según el rol del usuario autenticado.

    Args:
        Rol requerido para acceder a la función decorada. 

    Returns:
        Decorador que evalúa el rol del usuario actual.
        403 si el rol no coincide, de lo contrario ejecuta la función decorada.

    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            if current_user['role'] != role:
                return jsonify({"msg": "Acceso denegado"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator