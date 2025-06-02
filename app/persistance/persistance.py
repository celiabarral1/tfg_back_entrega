"""
Módulo principal de persistencia. Encapsulado en una clase porque almacena en una variable 
los datos del fichero generado, que representan los datos de análisis de la aplicación.
"""

import csv
from datetime import datetime, time
import os
import pandas as pd
from flask import current_app

# Módulo principal de persistencia. Encapsulado en una clase porque almacena en una variable 
# los datos del fichero generado, que representan los datos de análisis de la aplicación.
class RecordDataCSV:
    def __init__(self, file_path='resources/estocastic_data.csv'):
        self.file_path = file_path
        self.data, self.index, self.index_timestmap = self.load_records()

    def load_records(self):
        try:
            # Lee el archivo CSV completo como un DataFrame de pandas
            df = pd.read_csv(self.file_path, delimiter=';')
            # Convierte el DataFrame a una lista de diccionarios, similar a la salida json
            records = df.to_dict(orient='records')
            
             # Crear un índice para las búsquedas rápidas (diccionario de user_id -> registro)
            index = {}
            index_timestmap = {}
            for record in records:
                user_id = record['user_id']    # índice de user_id
                timestamp = int(record['timestamp'])   # índice por fecha para agilizar la búsqueda por fechas

                if user_id not in index:
                    index[user_id] = []
                index[user_id].append(record)

                if user_id not in index_timestmap:
                    index_timestmap[user_id] = []
                if timestamp:
                    index_timestmap[user_id].append((timestamp, record))  

            # index contiene para cada un user_id, sus registros (CLAVE, VALORES)
            return records, index, index_timestmap
        except FileNotFoundError:
            print(f"Archivo no encontrado.")
            return []
        except Exception as e:
            print(f"Ocurrió un error al leer el archivo: {e}")
            return []
        
    def get_user_ids(self):
        return sorted(set(record['user_id'] for record in self.data if 'user_id' in record))
    
    # Función que dado un user_id y un rango de fechas devuelve los datos asociados.
    # Proceso agilizado por la indexación de la función anterior.
    def filter_records_by_user_date(self, user_id,start_date, end_date):
        filtered_records = []
        
        # Verificamos si el user_id existe en el índice
        if user_id in self.index_timestmap:
            user_records = self.index_timestmap[user_id]
            
            for timestamp, record in user_records:
                record_date = datetime.fromtimestamp(timestamp)  # Convertir el timestamp a un objeto datetime

                # Filtrar los registros por el rango de fechas
                if start_date <= record_date <= end_date:
                    print(record_date)
                    filtered_records.append(record)
        # Ordenar los registros por fecha de la más antigua a la más nueva

        return filtered_records
    
    # Función que dado un turno y un rango de fechas devuelve los datos asociados.
    def filter_by_date_and_shift(self, start_date, end_date, shift):
        # Aseguramos que start_date siempre sea menor o igual a end_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        # Acceder a los turnos desde la configuración de la aplicación Flask
        shifts = current_app.config.get('SHIFTS', {})

        if shift not in shifts:
            raise ValueError(f"No existe ese turno")
        
        # shift_start, shift_end = shifts[shift]
        shift_start, shift_end = [self._parse_time(t) for t in shifts[shift]]
        filtered_records = []
        
        for record in self.data:
            record_datetime = datetime.fromtimestamp(record['timestamp'])
            
            # Comprobación del rango de fechas
            if start_date <= record_datetime <= end_date:
                record_time = record_datetime.time()
                
                # Comprobación de que se encuentra en la franja horaria del turno
                if shift == "noche":
                    if (record_time >= shift_start and record_time < time(23, 59, 59)) or (record_time >= time(0, 0) and record_time < shift_end):
                        filtered_records.append(record)
                else:
                    if shift_start <= record_time < shift_end:
                        filtered_records.append(record)
        
        return filtered_records
    
    def _parse_time(self, time_str):
        """Convierte una cadena de tiempo en un objeto `time`."""
        hours, minutes = map(int, time_str.split(":"))
        return time(hours, minutes)
    
    def get_emotions(self):
        emotions = set()  

        for record in self.data:
            emotions.add(record.get('Emotion_1_label', '').strip())
            emotions.add(record.get('Emotion_2_label', '').strip())
            emotions.add(record.get('Emotion_3_label', '').strip())
            
        return sorted(list(emotions))
    
