"""
analysis_controller.py

Módulo encargado de analizar la clasificación emocional de los trabajadores.
Lee el archivo CSV generado por el sistema y agrupa usuarios por su condición emocional estimada.

Blueprints:
    analysis_bp: Blueprint registrado bajo la ruta '/analysis'.

"""

from flask import Blueprint, jsonify
import pandas as pd

from app.module_analysis.analysis_processor import determine_condition

analysis_bp = Blueprint('analysis', __name__)

csv_path = "resources/estocastic_data_classified.csv"

# Endpoint que devuelve la clasificación de los trabajadores 
# según sus registros de csv_path 
@analysis_bp.route('/classify', methods=['GET'])
def classify_users_by_condition():
    """
    Lee el archivo de datos clasificados y agrupa los user_id por condición emocional.

    Returns:
        Devuelve un JSON con los ids de los usuarios agrupados por tendencia psicológica.
    """
    df = pd.read_csv(csv_path, sep=";")

    # Agrupar user_id por condición
    grouped_conditions = {
        "no_disorder": df[df["Predicted_Condition"] == "no_disorder"]["user_id"].tolist(),
        "depression": df[df["Predicted_Condition"] == "depression"]["user_id"].tolist(),
        "anxiety": df[df["Predicted_Condition"] == "anxiety"]["user_id"].tolist(),
    }

    return jsonify(grouped_conditions)

