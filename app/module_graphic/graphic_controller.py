"""
graphic_controller.py

Módulo Flask que gestiona los endpoints relacionados con la visualización de datos emocionales.
Permite consultar registros por usuario o turno, obtener listas de usuarios, emociones, turnos y periodos de tiempo.

Blueprints:
    graphic_bp: Blueprint que agrupa las rutas bajo /graphic.
"""

from flask import Blueprint, jsonify, request
from app.module_graphic.graphic_processor import GraphicProcessor, ShiftModel, TimeModel, date_range
from app.persistance.persistance import RecordDataCSV
import os

graphic_bp = Blueprint('graphic', __name__)

# data = RecordDataCSV()
# data_processor = GraphicProcessor(data)

data = None
data_processor = None

def load_default_data():
    """
    Carga de datos iniciales resources/estocastic_data.csv.
    """
    global data, data_processor
    data = RecordDataCSV(file_path='resources/estocastic_data.csv')
    data_processor = GraphicProcessor(data)

# Enpoint para recuperar los ids de los usuarios para analizar
@graphic_bp.route('/ids', methods=['GET'])
def get_ids():
    """
    Enpoint para recuperar los ids de los usuarios para analizar
    """
    return jsonify(data_processor.get_ids()), 200

# Endpoint que recoge los datos de una petición, 
# donde deben venir el user_id y una opción temporal
# Devuelve todos los datos asociados a ese trabajador y a ese rango temporal
@graphic_bp.route('/records/id', methods=['POST'])
def filter_records_by_id():
    """
    Endpoint que recoge los datos de una petición, donde deben venir el user_id y una opción temporal

    Returns:
        Los datos asociados a ese trabajador y a ese rango temporal
    """
    data = request.get_json()
    user_id = data.get('user_id')
    time_option = data.get('time_option')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    start_date_obj,end_date_obj = date_range(time_option,start_date,end_date)
    
    if not (start_date_obj and end_date_obj):
        return jsonify({"error": "No se proporcionó un rango de fechas válido"}), 400

    filtered_records = data_processor.filtered_by_id_time(int(user_id), start_date_obj, end_date_obj)

    return jsonify(filtered_records), 200

# Endpoint que recoge los datos de una petición, 
# donde deben venir el turno y una opción temporal
# Devuelve todos los datos asociados a un turno de trabajo en ese rango de fechas.
@graphic_bp.route('/records/shift', methods=['POST'])
def filter_records_by_shift():
    """
    Endpoint que recoge los datos de una petición, donde deben venir el turno y una opción temporal
    y filtra los datos acorde.

    Returns: 
        Los datos asociados a un turno de trabajo en ese rango de fechas.
    """
    print("Solicitud " ,request.get_json())
    data = request.get_json()
    shift = data.get('shift')  # "mañana", "tarde", "noche", "todos"
    time_option = data.get('time_option')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    start_date_obj,end_date_obj = date_range(time_option,start_date,end_date)

    if not (start_date_obj and end_date_obj):
        return jsonify({"error": "No se proporcionó un rango de fechas válido"}), 400

    filtered_records = data_processor.filtered_by_shift_time(shift,start_date_obj,end_date_obj)

    #saco los ids
    user_ids = list(set(record["user_id"] for record in filtered_records)) 

    return jsonify({
        "user_ids": user_ids,
        "data": filtered_records
    }), 200

# Endpoint que devuelve los tiempos de consulta más comunes y requeridos para consultar 
# análisis.
@graphic_bp.route('/getTimePeriods', methods=['GET'])
def get_time_periods():
    """
    Endpoint que devuelve los tiempos de consulta más comunes
    """
    time_model = TimeModel()
    return jsonify(time_model.get_time_options())  , 200

# Endpoint que devuelve los turnos de trabajo de la empresa
@graphic_bp.route('/getShifts', methods=['GET'])
def get_shifts():
    """
    Endpoint que devuelve los turnos de trabajo de la empresa
    """
    shiftModel = ShiftModel()
    return jsonify(shiftModel.get_shifts())  , 200

# Endpoint que devuelve las emociones categóricas que se analizan
@graphic_bp.route('/getEmotions', methods=['GET'])
def get_emotions():
    """
    Endpoint que devuelve las emociones categóricas que se analizan
    """
    return data_processor.get_all_emotions(), 200

@graphic_bp.route('/setCsv', methods=['POST'])
def set_csv():
    """
    Endpoint que modifica la muestra de datos que se analizan y explotan
    """
    global data, data_processor
    body = request.get_json()
    new_file = body.get("file")

    if not new_file:
        return jsonify({"error": "Falta el nombre del archivo"}), 400

    path = os.path.join('resources', new_file)

    if not os.path.exists(path):
        return jsonify({"error": "Archivo no encontrado"}), 404

    try:
        data = RecordDataCSV(file_path=path)
        data_processor = GraphicProcessor(data)
        return jsonify({"message": f"Fuente de datos cambiada a {new_file}"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al cargar datos: {e}"}), 500

