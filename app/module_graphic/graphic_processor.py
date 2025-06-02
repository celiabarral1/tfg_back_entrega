"""
graphic_processor.py

Módulo encargado de procesar, filtrar y estructurar los datos emocionales para su representación gráfica.
"""

from datetime import datetime
from datetime import datetime, timedelta
from flask import current_app
class GraphicProcessor:
    """
    Clase encargada de filtrar los datos para su representación
    """
    def __init__(self, data_source):
        # data_source es una instancia de RecordDataCSV u otra fuente de datos similar
        self.data_source = data_source
        self.records = self.data_source.data # Lee los datos iniciales
        self.index = self.data_source.index  # Accede al índice de user_id

    def get_all_records(self):
        """
        Devuelve todos las grabaciones del dataset.
        """
        # Devuelve todos las filas, las grabaciones
        return self.records
    
    def get_ids(self):
        """
        Obtiene todos los IDs de usuarios registrados.

        """
        return self.data_source.get_user_ids()

    def find_records_by_id(self, user_id):
        """
        Devuelve los datos para un user_id, las grabaciones.
        """
        return self.index.get(user_id, [])
    
    # Grabaciones filtradas por id y espacios temporales definidos en TimeModel
    def filtered_by_id_time(self,user_id, start_date,finish_date):
        """
        Filtra registros por user_id y rango de fechas.
        """
        return self.data_source.filter_records_by_user_date(user_id, start_date, finish_date)
    
    def filtered_by_shift_time(self,shift, start_date,finish_date):
        """
        Filtra registros por turno y rango de fechas.
        """
        return self.data_source.filter_by_date_and_shift(start_date, finish_date,shift)

    def get_all_emotions(self):
        """
        Devuelve  las emociones categóricas
        """
        return self.data_source.get_emotions()
    

    
class TimeModel:
    """
    Clase para gestionar las opciones de rango de tiempo.
    """
    def __init__(self):
        self.options = [
            {"label": "15 días", "value": "15d"},
            {"label": "1 mes", "value": "1m"},
            {"label": "3 meses", "value": "3m"},
            {"label": "1 año", "value": "1y"}
        ]

    def get_time_options(self):
        """
        Devuelve las opciones de tiempo disponibles.
        """
        return self.options
    
    def get_time_range(self, option_value):
        """
        Convierte un valor de opción en un rango real de fechas.
        """
        now = datetime.now()
        
        if option_value == "15d":
            start_date = now - timedelta(days=15)
        elif option_value == "1m":
            start_date = now - timedelta(days=30)
        elif option_value == "3m":
            start_date = now - timedelta(days=90)
        elif option_value == "6m":
            start_date = now - timedelta(days=180)
        elif option_value == "1y":
            start_date = now - timedelta(days=365)
        else:
            raise ValueError("Opción no válida")

        return {"start_date": start_date, "end_date": now}


class ShiftModel:
    """
    Modelo que retorna los turnos de trabajo disponibles definidos en la configuración.
    """
    def __init__(self):
        # Obtener los turnos desde la configuración de Flask
        shifts_config = current_app.config.get('SHIFTS', {})
        
        # Crear las opciones dinámicamente usando la configuración
        self.options = [
            {"label": f"{shift.capitalize()} ({start} - {end})", "value": shift}
            for shift, (start, end) in shifts_config.items()
        ]

    def get_shifts(self):
        """
        Devuelve la lista de turnos de trabajo configurados.
        """
        return self.options
    
def date_range(time_option, start_date, end_date):
    """
    Devuelve un rango de fechas interpretando opciones o fechas personalizadas.
    """
    start_date_obj = None
    end_date_obj = None

    if time_option:
        time_service = TimeModel()
        time_range = time_service.get_time_range(time_option)
        start_date_obj = time_range["start_date"]
        end_date_obj = time_range["end_date"]
    elif start_date and end_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    return start_date_obj,end_date_obj