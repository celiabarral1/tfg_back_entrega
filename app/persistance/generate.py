"""
Módulo encargado de la generación de muestras de datos emocionales representativos de la población española trabajadora.
Se basa en una función estocástica que contempla:
    E(t) (evolución por hora de un estado psicológico) ,el nivel emocional, 
    la influencia del clima, los ritmos circadianos y eventos aleatorios.
Todo ello se combina para dar unos valores emocionales categóricos y dimensionales que se adecuen a los porcentajes 
de tendencia psicológica que deben representarse, asociando el peso de las emociones con una condición.
"""

from datetime import datetime
import json
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import sys
import os
from flask import current_app

# Añadir el path raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.config.config import Config

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
default_config_path = os.path.join(base_path, 'resources', 'config', 'config.json')
new_config_path = os.path.join(base_path, 'resources', 'config', 'new_config.json')

print(default_config_path)

# 1. Cargar valores por defecto desde config.json
with open(default_config_path, 'r', encoding='utf-8') as f:
    default_config = json.load(f)
default_gen = default_config.get("GENERATION", {})

# 2. Inicializar con los valores por defecto
n_workers = default_gen.get("n_workers", 100)
n_samples = default_gen.get("n_samples", 10000)

# 3. Si existe new_config.json, usar sus valores para sobrescribir
if os.path.exists(new_config_path):
    with open(new_config_path, 'r', encoding='utf-8') as f:
        new_config = json.load(f)
    new_gen = new_config.get("GENERATION", {})
    n_workers = new_gen.get("n_workers", n_workers)
    n_samples = new_gen.get("n_samples", n_samples)

print(f"Configuración final: n_workers = {n_workers}, n_samples = {n_samples}")

# Módulo ejecutable de los datos emocionales que se analizarán y representarán en el sistema
# Salida generada en resourcer/resources/estocastic_data.csv

# Definir la función estocástica E(t), evolución por hora de un estado psicológico
# Interviene el nivel emocional, la influencia del clima, los ritmos circadianos y eventos aleatorios
def compute_E(t, baseline, weather_influence, circadian_amplitude, random_event_magnitude):
    """
    Función estocástica para calcular E(t): estado emocional en el tiempo.
    """
    circadian = circadian_amplitude * np.sin(2 * np.pi * t / 24)  
    random_events = np.random.normal(0, random_event_magnitude, len(t))  
    noise = np.random.normal(0, 0.1, len(t)) 
    E_t = baseline + weather_influence + circadian + random_events + noise
    return E_t

# Configuración de parámetros para los diferentes estados psicológicos
params = {
    "no_disorder": {"baseline": 0.5, "weather_influence": 0.2, "circadian_amplitude": 0.3, "random_event_magnitude": 0.1},
    "depression": {"baseline": -0.5, "weather_influence": -0.1, "circadian_amplitude": 0.2, "random_event_magnitude": 0.2},
    "anxiety": {"baseline": -0.2, "weather_influence": 0.1, "circadian_amplitude": 0.4, "random_event_magnitude": 0.3},
}

# Generar la evolución de E(t) para un día completo (24 horas)
hours = np.linspace(0, 24, 1000)
E_t_data = {condition: compute_E(hours, **params[condition]) for condition in params.keys()}

# Crear IDs de trabajadores y asignarles una condición con los nuevos porcentajes
# n_workers = current_app.config.get('GENERATION', {}).get('n_trabajadores', 100)
# n_workers = Config.get_n_workers()

# Representación de porcentajes trastornos psicológicos en la población 
# española trabajadora
depression_percentage = 5.4 / 100
anxiety_percentage = 6.7 / 100
no_disorder_percentage = 1 - (depression_percentage + anxiety_percentage)

worker_conditions = (
    [0] * int(no_disorder_percentage * n_workers) +  # Sin trastornos
    [1] * int(depression_percentage * n_workers) +   # Depresión
    [2] * int(anxiety_percentage * n_workers)        # Ansiedad
)
random.shuffle(worker_conditions)
worker_to_condition = dict(zip(range(1, n_workers + 1), worker_conditions)) # Genra una condición teniendo en cuenta el pocentaje

# Mapa de valores para emociones categóricas
emotion_weights = {
    "no_disorder": {"neutral": (30, 50), "happiness": (20, 40), "sadness": (10, 20), "fear": (5, 15), "anger": (5, 10), "disgust": (5, 10)},
    "depression": {"sadness": (40, 50), "disgust": (10, 20), "anger": (10, 15), "fear": (5, 15), "neutral": (10, 15), "happiness": (0, 5)},
    "anxiety": {"fear": (40, 60), "sadness": (10, 20), "anger": (5, 15), "disgust": (5, 10), "neutral": (5, 15), "happiness": (5, 10)},
}

# Elige el valor de las emociones para que coincidan con la condición que recibe como parámetro
def choose_emotion(condition):
    weights = emotion_weights[condition]
    labels = list(weights.keys())
    probabilities = [np.random.uniform(low, high) for low, high in weights.values()]
    probabilities = np.array(probabilities) / sum(probabilities)  # Normalizar
    return np.random.choice(labels, p=probabilities)

# Mapa de valores para dimensiones emocionales
emotion_dimension_map = {
    "happiness": {"arousal": (0.3, 0.7), "valence": (0.5, 1.0), "dominance": (0.5, 1.0)},
    "sadness": {"arousal": (0.0, 0.3), "valence": (-1.0, -0.5), "dominance": (-0.7, -0.3)},
    "fear": {"arousal": (0.6, 1.0), "valence": (-1.0, -0.5), "dominance": (-1.0, -0.6)},
    "disgust": {"arousal": (0.4, 0.8), "valence": (-1.0, -0.5), "dominance": (-0.7, -0.4)},
    "anger": {"arousal": (0.7, 1.0), "valence": (-0.7, -0.3), "dominance": (-0.5, -0.2)},
    "neutral": {"arousal": (0.2, 0.5), "valence": (-0.1, 0.1), "dominance": (0.0, 0.3)},
}

# Recibe cada emoción categórica, asociada a una condición y le da valores aleatorios a las dimensionales dentro
# de los rangos establecidos
def assign_dimensions(emotion):
    ranges = emotion_dimension_map[emotion]
    arousal = np.random.uniform(*ranges["arousal"])
    valence = np.random.uniform(*ranges["valence"])
    dominance = np.random.uniform(*ranges["dominance"])
    return arousal, valence, dominance

# Generar los datos entre el 1 de enero de 2024 y el 31 de enero de 2025
# n_samples = current_app.config.get('GENERATION', {}).get('n_samples', 10000)
# n_samples = Config.get_n_samples()
start_date = datetime(2024, 1, 1, 0, 0, 0)
end_date = datetime(2025, 12, 31, 23, 59, 59)

# Generar una lista de timestamps en orden creciente
timestamps = np.linspace(
    int(start_date.timestamp()), 
    int(end_date.timestamp()), 
    n_samples
).astype(int)

data = []
for i, timestamp in enumerate(timestamps):
    file_name = f"{timestamp}_{i}.wav"
    user_id = random.choice(list(worker_to_condition.keys()))
    condition = worker_to_condition[user_id]
    condition_name = ["no_disorder", "depression", "anxiety"][condition]
    
    # Obtener E(t) promedio para cada condición
    E_t = np.mean(E_t_data[condition_name])
    
    # Elegir emociones categóricas y ajustar dimensiones
    emotion_1_label = choose_emotion(condition_name)
    arousal_1, valence_1, dominance_1 = assign_dimensions(emotion_1_label)
    emotion_2_label = choose_emotion(condition_name)
    arousal_2, valence_2, dominance_2 = assign_dimensions(emotion_2_label)
    emotion_3_label = choose_emotion(condition_name)
    arousal_3, valence_3, dominance_3 = assign_dimensions(emotion_3_label)
    
    # Generar datos emocionales
    emotion_data = (
        max(0, min(1, round(E_t + np.random.uniform(0, 0.5), 9))),  # Emotion_1_mean
        max(0, min(1, round(np.random.uniform(0, 0.1), 9))),        # Emotion_1_std
        emotion_1_label,
        max(0, min(1, round(E_t + np.random.uniform(0, 0.5), 9))),  # Emotion_2_mean
        max(0, min(1, round(np.random.uniform(0, 0.1), 9))),        # Emotion_2_std
        emotion_2_label,
        max(0, min(1, round(E_t + np.random.uniform(0, 0.5), 9))),  # Emotion_3_mean
        max(0, min(1, round(np.random.uniform(0, 0.1), 9))),        # Emotion_3_std
        emotion_3_label,
        arousal_1, valence_1, dominance_1
    )
    
    data.append((file_name, timestamp, user_id, *emotion_data))

# Cabecera del archivo .csv
columns = [
    "file_name", "timestamp", "user_id",
    "Emotion_1_mean", "Emotion_1_std", "Emotion_1_label",
    "Emotion_2_mean", "Emotion_2_std", "Emotion_2_label",
    "Emotion_3_mean", "Emotion_3_std", "Emotion_3_label",
    "arousal", "valence", "dominance"
]
df = pd.DataFrame(data, columns=columns)


# Guardar el csv. 
# Archivo de datos principal del sistema
output_file = "resources/estocastic_data_reconfig.csv"
df.to_csv(output_file, index=False, sep=";")


print(f"CSV generado: {output_file}")
