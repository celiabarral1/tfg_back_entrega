"""
config_controller.py

Este módulo permite consultar, actualizar y resetear la configuración global de la aplicación Flask.
Expone endpoints que permiten obtener la configuración actual, actualizarla dinámicamente
y persistir los cambios en un archivo JSON, incluyendo la ejecución de un script externo.

Blueprints:
    config_bp: Blueprint de configuración de la app.

"""
from flask import Blueprint, json, jsonify, current_app, request, jsonify
import os
import subprocess

from app.config.config import Config

config_bp = Blueprint('config', __name__)

@config_bp.route('/getConfig', methods=['GET'])
def get_config():
    """
    Devuelve en JSON la configuración de la aplicación.

    """
    config_data = {
        "DEBUG": current_app.config.get("DEBUG"),
        "JWT_SECRET_KEY": current_app.config.get("JWT_SECRET_KEY"),
        "SECRET_KEY": current_app.config.get("SECRET_KEY"),
        "CORS_ORIGINS": current_app.config.get("CORS_ORIGINS"),
        "UPLOAD_FOLDER": current_app.config.get("UPLOAD_FOLDER"),
        "MAX_CONTENT_LENGTH": current_app.config.get("MAX_CONTENT_LENGTH"),
        "PORT": current_app.config.get("PORT"),
        "PORT_FORCE_ALIGNMENT": current_app.config.get("PORT_FORCE_ALIGNMENT"),
        "SHIFTS": current_app.config.get("SHIFTS"),
        "GENERATION": current_app.config.get("GENERATION"),
        "INFERENCE": current_app.config.get("INFERENCE")
    }

    return jsonify(config_data)


@config_bp.route('/changeConfig', methods=['POST'])
def change_config():
    """
    Actualiza dinámicamente la configuración de la app y la guarda.

    Returns:
        Mensaje de confirmación o notificar que no se reciben datos.
    """
    # Obtén la nueva configuración desde la solicitud
    new_config = request.get_json()

    if not new_config:
        return jsonify({"error": "No se reciben datos."}), 400
    
    print(new_config)

    # Actualiza la configuración global de la aplicación (Flask)
    current_app.config['GENERATION'] = new_config.get('GENERATION', current_app.config.get('GENERATION', {}))
    current_app.config['INFERENCE'] = new_config.get('INFERENCE', current_app.config.get('INFERENCE', {}))

    # Asegúrate de que los valores no se sobrescriban si no están presentes
    current_app.config['GENERATION']['n_trabajadores'] = new_config.get('GENERATION', {}).get('n_workers', current_app.config['GENERATION'].get('n_trabajadores', 100))
    current_app.config['GENERATION']['n_samples'] = new_config.get('GENERATION', {}).get('n_samples', current_app.config['GENERATION'].get('n_samples', 100))

    current_app.config['INFERENCE']['silence_interval'] = new_config.get('INFERENCE', {}).get('silence_interval', current_app.config['INFERENCE'].get('silence_interval', 10))
    current_app.config['INFERENCE']['inference_model'] = new_config.get('INFERENCE', {}).get('inference_model', current_app.config['INFERENCE'].get('inference_model', 'default_model'))

# Construir la ruta para guardar el archivo en app/resources/config
    base_dir = os.path.abspath(os.path.dirname(__file__))  # Ruta actual
    config_folder = os.path.join(base_dir, '..', '..', 'resources', 'config')
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)  # Crear la carpeta si no existe

    new_config_path = os.path.join(config_folder, 'new_config.json')

     # Guardar la nueva configuración en un archivo JSON
    with open(new_config_path, 'w', encoding='utf-8') as f:
        json.dump(new_config, f, indent=2, ensure_ascii=False)

    # Recargar la configuración de la aplicación con el nuevo archivo
    Config.init_app(current_app, config_filename='new_config.json')

   
    # Construir la ruta absoluta al script
    script_path = os.path.join(os.path.dirname(__file__), '..', 'persistance', 'generate.py')
    script_path = os.path.abspath(script_path)

    # Ejecutar generate.py con la nueva configuración
    subprocess.run(['python', script_path])

    return jsonify({"message": "Config guardada con éxito"}), 200



@config_bp.route('/resetConfig', methods=['GET'])
def reset_config():
    # Recargar la configuración de la aplicación con el nuevo archivo
    Config.init_app(current_app, config_filename='config.json')

    return jsonify({"message": "Config guardada con éxito"}), 200
