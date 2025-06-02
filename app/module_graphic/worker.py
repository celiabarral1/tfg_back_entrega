from datetime import datetime

class Worker:
    """
    Clase que encapsula las prioridades de un trabajador a analizar.
    """
    def __init__(self, id, workstation, date_contratation, rol=None, register_date=None):
        self.id = id
        self.workstation = workstation
        self.date_contratation = datetime.strptime(date_contratation, '%Y-%m-%d') if isinstance(date_contratation, str) else date_contratation
        self.rol = rol
        self.register_date = datetime.strptime(register_date, '%Y-%m-%d') if isinstance(register_date, str) else register_date

    def to_dict(self):
        """
        Convierte el objeto Worker a un diccionario.
        :return: Diccionario con los datos del trabajador.
        """
        return {
            'id': self.id,
            'workstation': self.workstation,
            'date_contratation': self.date_contratation.strftime('%Y-%m-%d'),
            'rol': self.rol,
            'register_date': self.register_date.strftime('%Y-%m-%d') if self.register_date else None
        }

class RolModel:
    
    def __init__(self):
        self.options = [
            {"label": "Operario autorizado", "value": "operario"},
            {"label": "Psicólogo", "value": "psicólogo"}
        ]

    def get_rols(self):
        return self.options
