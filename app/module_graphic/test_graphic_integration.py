import tempfile
from unittest.mock import MagicMock
import pytest
import json
import os
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from app.module_graphic.graphic_controller import graphic_bp
from app.module_graphic.graphic_processor import GraphicProcessor, date_range
from app.persistance.persistance import RecordDataCSV


@pytest.fixture
def app():
    """ Configura una aplicación Flask de prueba """
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test_key"  
    app.register_blueprint(graphic_bp, url_prefix="/graphic")
    
    jwt = JWTManager(app)

    return app

@pytest.fixture
def client(app):
    """ Proporciona un cliente de prueba para realizar peticiones HTTP """
    return app.test_client()

@pytest.fixture
def mock_data():
    # Fixture para simular los datos de RecordDataCSV si es necesario
    mock_data = RecordDataCSV()

    data_processor = GraphicProcessor(mock_data)
    return data_processor

def test_get_ids(client, mock_data):
    """ Verifica el endpoint '/graphic/ids' """
    # Simulamos la respuesta esperada de 'get_ids'
    expected_ids = mock_data.get_ids()  # Asegúrate de que get_ids() esté definido y devuelva algo válido
    response = client.get('/graphic/ids')
    
    assert response.status_code == 200
    print(response.json)
    assert response.json == expected_ids  # Verifica que los ids retornados sean los esperados

def test_filter_records_by_id(client, mock_data):
    """ Verifica el endpoint '/graphic/records/id' """
    # Simulamos los datos que enviará el cliente
    request_data = {
        'user_id': 1,
        'time_option': '1y'
    }

    start_date, end_date = date_range('1y',None,None)
    # Simulamos los resultados filtrados por id
    expected_filtered_records = mock_data.filtered_by_id_time(1, start_date, end_date)  # Ajusta esto a lo que deberías esperar

    response = client.post('/graphic/records/id', json=request_data)

    assert response.status_code == 200
    assert response.json == expected_filtered_records  # Verifica los registros filtrados

def test_filter_records_by_shift(client, mock_data):
    """ Verifica el endpoint '/graphic/records/shift' """
    request_data = {
        'shift': 'mañana',
        'start_date': '2024-10-11',
        'end_date': '2024-12-07'
    }

    start_date, end_date = date_range(None,'2024-10-11','2024-12-07')

    # Simula los registros filtrados por turno
    expected_filtered_records = mock_data.filtered_by_shift_time('mañana',start_date, end_date)  # Ajusta según tus datos
    expected_user_ids = list(set(record["user_id"] for record in expected_filtered_records))

    response = client.post('/graphic/records/shift', json=request_data)

    assert response.status_code == 200
    assert 'user_ids' in response.json
    assert set(response.json['user_ids']) == set(expected_user_ids)
    assert 'data' in response.json
    assert response.json['data'] == expected_filtered_records

def test_get_time_periods(client):
    """ Verifica el endpoint '/graphic/getTimePeriods' """
    response = client.get('/graphic/getTimePeriods')

    assert response.status_code == 200
    assert isinstance(response.json, list)  # Asegúrate de que sea una lista de opciones de tiempo

def test_get_shifts(client):
    """ Verifica el endpoint '/graphic/getShifts' """
    response = client.get('/graphic/getShifts')

    assert response.status_code == 200
    assert isinstance(response.json, list)  # Asegúrate de que sea una lista de turnos

def test_get_emotions(client, mock_data):
    """ Verifica el endpoint '/graphic/getEmotions' """
    response = client.get('/graphic/getEmotions')

    assert response.status_code == 200
    assert 'anger' in response.json 
    assert 'happiness' in response.json
    assert 'fear' in response.json
    assert 'neutral' in response.json
    assert 'sadness' in response.json
    assert 'disgust' in response.json
