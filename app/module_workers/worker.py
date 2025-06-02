from datetime import datetime
"""
Entidad Trabajador para manejar los registros de trabajadores del sistema
"""
# Entidad Trabajador para manejar los registros de trabajadores del sistema
class Worker:
    # Id, puesto de trabajo que ocupa, fecha en la que fue contratado, rol y fecha de alta en la aplicación
    def __init__(self, id, workstation, hiring_date, rol=None, register_date=None):
        self.id = id
        self.workstation = workstation
        self.hiring_date = datetime.strptime(hiring_date, '%Y-%m-%d') if isinstance(hiring_date, str) else hiring_date
        self.rol = rol
        self.register_date = datetime.strptime(register_date, '%Y-%m-%dT%H:%M:%S.%fZ') if isinstance(register_date, str) and register_date else None

# Entidad Rol para gestionar los roles existentes
class RolModel:
    def __init__(self):
        self.options = [
            {"label": "Operario autorizado", "value": "operario"},
            {"label": "Psicólogo", "value": "psicólogo"}
        ]

    def get_rols(self):
        return self.options
