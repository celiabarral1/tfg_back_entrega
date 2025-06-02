import base64
import logging
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import pandas as pd
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory, Blueprint
from app.config.config import Config
import atexit
import os
 
app = Flask(__name__)
Config.init_app(app)

app.config.from_object(Config)

logging.basicConfig(level=logging.INFO)
# app.debug = True
# app.debug = app.config['DEBUG']

CORS(app)

# AUTENTICACIÓN
# app.config['JWT_SECRET_KEY'] = 'web_emotions_jwt_154!.???' 
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Importar módulos
from app.auth.auth_controller import auth_bp
from app.module_analysis.analysis_controller import analysis_bp
from app.module_workers.worker_controller import workers_bp
from app.module_inference.audio_controller import audio_bp
from app.module_graphic.graphic_controller import graphic_bp
from app.config.config_controller import config_bp

# Registrar Blueprints 
app.register_blueprint(auth_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(workers_bp)
app.register_blueprint(audio_bp)
app.register_blueprint(graphic_bp)
app.register_blueprint(config_bp)

from app.module_graphic.graphic_controller import load_default_data
# Cargar datos por defecto una vez al iniciar la app
load_default_data()

@atexit.register
def cleanup_config():
    config_path = os.path.join(os.getcwd(),'resources', 'config', 'new_config.json')
    print(config_path)
    if os.path.exists(config_path):
        os.remove(config_path)
        print("Archivo new_config.json eliminado.")
    
if __name__ == "__main__":
    # classify_conditions_by_user('resources/estocastic_data.csv')
    app.run(port=app.config.get("PORT", 5000))