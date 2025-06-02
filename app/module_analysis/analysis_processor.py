"""
analysis_processor.py

Este módulo contiene la lógica para determinar la condición emocional predominante
de un usuario, en base a sus registros categóricos y dimensionales de emociones.

"""

import os
import pandas as pd
import numpy as np

# Rangos de emociones categóricas y dimensiones emocionales para cada condición
# Pesos para cada emoción según el trastorno
emotion_weights = {
    "no_disorder": {"neutral": (30, 50), "happiness": (20, 40), "sadness": (10, 20), "fear": (5, 15), "anger": (5, 10), "disgust": (5, 10)},
    "depression": {"sadness": (40, 50), "disgust": (10, 20), "anger": (10, 15), "fear": (5, 15), "neutral": (10, 15), "happiness": (0, 5)},
    "anxiety": {"fear": (40, 60), "sadness": (10, 20), "anger": (5, 15), "disgust": (5, 10), "neutral": (5, 15), "happiness": (5, 10)},
}

# Relación establecia entre cada emoción categórica y las tres dimensionales
emotion_dimension_map = {
    "happiness": {"arousal": (0.3, 0.7), "valence": (0.5, 1.0), "dominance": (0.5, 1.0)},
    "sadness": {"arousal": (0.0, 0.3), "valence": (-1.0, -0.5), "dominance": (-0.7, -0.3)},
    "fear": {"arousal": (0.6, 1.0), "valence": (-1.0, -0.5), "dominance": (-1.0, -0.6)},
    "disgust": {"arousal": (0.4, 0.8), "valence": (-1.0, -0.5), "dominance": (-0.7, -0.4)},
    "anger": {"arousal": (0.7, 1.0), "valence": (-0.7, -0.3), "dominance": (-0.5, -0.2)},
    "neutral": {"arousal": (0.2, 0.5), "valence": (-0.1, 0.1), "dominance": (0.0, 0.3)},
}

# Función para determinar la condición basándose en emociones categóricas y dimensiones emocionales
# Parámetro de entrada los datos de un user_id
# Calcula para los datos de un usauario, una puntuación para cada condición 
# La puntuación se calcula 
# Devuelve la condición, la condición más puntuada
def determine_condition(rows):
    """
    Determina la condición emocional dominante de un usuario basándose en emociones categóricas y dimensiones emocionales

    Args:
        user_id.

    Returns:
        Condición emocional estimada
    """
    emotion_columns = ["Emotion_1_label", "Emotion_2_label", "Emotion_3_label"]
    dimensions = ["arousal", "valence", "dominance"]

    emotion_counts = {"no_disorder": 0, "depression": 0, "anxiety": 0}
    dimension_scores = {"no_disorder": 0, "depression": 0, "anxiety": 0}

    # Para cada fila, saca los 3 nombres de las emociones categóricas y 
    # las clasifica, según el rango en el que esté en relación con lo definido en emotion_weights
    for _, row in rows.iterrows():
        for condition, emotions in emotion_weights.items():
            for emotion in row[emotion_columns]:
                if emotion in emotions:
                    weight_range = emotions[emotion]
                    weight = np.random.uniform(weight_range[0], weight_range[1])
                    emotion_counts[condition] += weight

        # Pra cada emoción se extraen los valores de arousal, valence y dominance y 
        # comprueba si están dentro de los rango para la emoción en la condición que se le asoció
        # en el bucle de arriba.
        # Si es que si, aumenta el contador de la condición
        for emotion in row[emotion_columns]:
            if emotion in emotion_dimension_map:
                for dimension in dimensions:
                    dim_value = row[dimension]
                    dim_range = emotion_dimension_map[emotion][dimension]
                    if dim_range[0] <= dim_value <= dim_range[1]:
                        for condition in dimension_scores.keys():
                            if emotion in emotion_weights[condition]:
                                dimension_scores[condition] += 1

    # Normalizar, dividir entre 0 y 1
    total_emotion_counts = sum(emotion_counts.values())
    total_dimension_scores = sum(dimension_scores.values())

    #
    if total_emotion_counts > 0:
        emotion_counts = {k: v / total_emotion_counts for k, v in emotion_counts.items()}
    if total_dimension_scores > 0:
        dimension_scores = {k: v / total_dimension_scores for k, v in dimension_scores.items()}

    # Combinar las coincidencias de emocional y dimensional. La que más se ameje, sale como condición.
    final_scores = {
        condition: emotion_counts[condition] + dimension_scores[condition]
        for condition in emotion_counts.keys()
    }

    return max(final_scores, key=final_scores.get)

# Cargar el CSV y predecir las condiciones agrupadas por user_id
def classify_users_by_condition(csv_path):
    """
    Aplica la función la función determine_condition() a cada usuario del archivo CSV.

    """
    if not os.path.exists(csv_path):
        print(f"Error: El archivo {csv_path} no existe.")
        return
    
    # Verificar carga correcta del archivo csv
    try:
        df = pd.read_csv(csv_path, sep=";")
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    # Clasificar por user_id
    user_groups = df.groupby("user_id")
    user_conditions = user_groups.apply(determine_condition).reset_index()
    user_conditions.columns = ["user_id", "Predicted_Condition"]

    # Guardar resultados en un csv de igual nombre al dado para analizar pero acabado en _classified.
    # estocastic_data_classified.csv
    output_path = csv_path.replace(".csv", "_classified.csv")
    user_conditions.to_csv(output_path, index=False, sep=";")
    print(f"Archivo guardado en: {output_path}")

