
from io import BytesIO
import os
from flask import Flask
from flask_jwt_extended import JWTManager
import pytest
from app.module_inference.audio_controller import audio_bp

@pytest.fixture
def app():
    """ Configura una aplicación Flask de prueba """
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test_key" 
    app.register_blueprint(audio_bp, url_prefix="/audios")
    
    jwt = JWTManager(app)

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_data_audio(client):
    # Preparar un archivo de audio de prueba. Este puede ser un archivo WAV real o simulado.
    # Para este ejemplo, usaré un archivo WAV vacío o un archivo que puedas preparar como audio de prueba.
    
    audio_file_path = 'resources/audios/recording1.wav'  # Asegúrate de tener este archivo de prueba o usa uno real.
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"No se encuentra el archivo de prueba {audio_file_path}")
    
    # Abrir el archivo de audio de prueba
    with open(audio_file_path, 'rb') as f:
        audio_file = BytesIO(f.read())  # Leerlo en memoria
        audio_file.filename = 'recording1.wav'
        audio_file.content_type = 'audio/wav'
        
        # Hacer la solicitud POST con el archivo de audio
        response = client.post('/audio/getData', data={'audioFile': audio_file})

    # Verificar que la respuesta tenga el status 200
    assert response.status_code == 200
    
    # Obtener la respuesta JSON
    json_response = response.get_json()

    # Verificar que la respuesta contenga las claves esperadas
    assert 'message' in json_response
    assert 'transcription' in json_response
    assert 'normalized' in json_response
    assert 'alignments' in json_response
    assert 'emotions' in json_response

    # Verificar que el mensaje de éxito esté presente
    assert json_response['message'] == 'Audio test_audio.wav processed successfully'

def test_get_data_audio_no_file(client):
    # Hacer la solicitud POST sin archivo de audio
    response = client.post('/audio/getData')

    # Verificar que el status code sea 400
    assert response.status_code == 400

    # Verificar el mensaje de error
    json_response = response.get_json()
    assert json_response['message'] == 'No se encontró el audio'
