"""
config.py

Clase auxiliar para cargar, acceder y gestionar la configuración de la aplicación Flask desde archivos JSON.

"""

import json
import os
from flask import current_app

class Config:
    """
    Clase que encaplsula la configuración de la aplicación.
    """
    @staticmethod
    def init_app(app, config_filename='config.json'):
        """
        Carga configuración desde un archivo JSON y rellena el objeto.

        """
        base_dir = os.path.abspath(os.path.dirname(__file__))  # -> app
        config_path = os.path.join(base_dir, '..', '..', 'resources', 'config', config_filename)
        config_path = os.path.abspath(config_path)  # convierte a ruta absoluta

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No se encontró el archivo de configuración en: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        app.config.update(config_data)

    @staticmethod
    def get_port():
        return current_app.config.get('PORT', 5000)

    @staticmethod
    def get_n_workers():
        return current_app.config.get('GENERATION', {}).get('n_trabajadores', 100)

    @staticmethod
    def get_n_samples():
        return current_app.config.get('GENERATION', {}).get('n_samples', 10000)

    @staticmethod
    def get_silence_interval():
        return current_app.config.get('INFERENCE', {}).get('silence_interval', 500)

    @staticmethod
    def get_inference_model():
        return current_app.config.get('INFERENCE', {}).get('inference_model', 'model_ours_MIXED')
    
    @staticmethod
    def get_shifts_morning():
        return current_app.config.get('SHIFTS', {}).get('mañana')
    
    @staticmethod
    def get_shifts_afternoon():
        return current_app.config.get('SHIFTS', {}).get('tarde')
    
    @staticmethod
    def get_shifts_night():
        return current_app.config.get('SHIFTS', {}).get('noche')
    
    

