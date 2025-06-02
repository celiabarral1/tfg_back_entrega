from flask import Blueprint, jsonify, request
from app.module_workers.worker import RolModel, Worker
from app.module_workers.workers_processor import WorkersProcessor
from app.persistance.worker_persistance import WorkersDataCSV

workers_bp = Blueprint('workers', __name__)

worker_treatment = WorkersDataCSV('resources/register_of_workers.csv')
processor = WorkersProcessor(worker_treatment)

# Endpoint que devuelve los roles del sistema
@workers_bp.route('/getRols', methods=['GET'])
def get_roles():
    roles = RolModel()
    return jsonify(roles.get_rols())

# Endpoint que devuelve los ids de los trabajadores disponibles para dar
# de alta
@workers_bp.route('/workers/getIds', methods=['GET'])
def get_ids_no_rol():
    return jsonify(processor.get_workers_no_role())

# Endpoint para registrar a un trabajador.
# En este caso como el trabajador ya existe, modifca su rol de acceso a la web
@workers_bp.route('/workers/register', methods=['POST'])
def register_worker():
    data = request.json
    print(data)
    existing_worker = processor.find_worker_by_id(data['id'])

    if existing_worker:
        print('existe')
        processor.update_worker(data['id'], data['rol'], data['registrationDate'])
    else:
        return jsonify({"message": "No hay trabajadores con ese id"}), 400

    return jsonify({"message": "Trabajador registrado"}), 201