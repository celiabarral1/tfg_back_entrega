"""
classify_emotions_by_user.py

Script que clasifica la condición emocional entre depresión, ansiedad o ninguna
de cada usuario según sus emociones categóricas y dimensiones emocionales.

Entrada:
    CSV con emociones por usuario, etiquetas categóricas y dimensiones.

Salida:
    CSV clasificatorio, para cada user_id su condición

"""

import pandas as pd
import numpy as np

# Rangos de emociones categóricas y dimensiones emocionales para cada condición
emotion_weights = {
    "no_disorder": {"neutral": (30, 50), "happiness": (20, 40), "sadness": (10, 20), "fear": (5, 15), "anger": (5, 10), "disgust": (5, 10)},
    "depression": {"sadness": (40, 50), "disgust": (10, 20), "anger": (10, 15), "fear": (5, 15), "neutral": (10, 15), "happiness": (0, 5)},
    "anxiety": {"fear": (40, 60), "sadness": (10, 20), "anger": (5, 15), "disgust": (5, 10), "neutral": (5, 15), "happiness": (5, 10)},
}

emotion_dimension_map = {
    "happiness": {"arousal": (0.3, 0.7), "valence": (0.5, 1.0), "dominance": (0.5, 1.0)},
    "sadness": {"arousal": (0.0, 0.3), "valence": (-1.0, -0.5), "dominance": (-0.7, -0.3)},
    "fear": {"arousal": (0.6, 1.0), "valence": (-1.0, -0.5), "dominance": (-1.0, -0.6)},
    "disgust": {"arousal": (0.4, 0.8), "valence": (-1.0, -0.5), "dominance": (-0.7, -0.4)},
    "anger": {"arousal": (0.7, 1.0), "valence": (-0.7, -0.3), "dominance": (-0.5, -0.2)},
    "neutral": {"arousal": (0.2, 0.5), "valence": (-0.1, 0.1), "dominance": (0.0, 0.3)},
}

# Función para determinar la condición basándose en emociones categóricas y dimensiones emocionales
def determine_condition(rows):
    """
    Clasifica la condición emocional de un usuario según sus emociones categóricas y dimensiones.
    """
    emotion_columns = ["Emotion_1_label", "Emotion_2_label", "Emotion_3_label"]
    dimensions = ["arousal", "valence", "dominance"]

    # Inicializar conteos y puntajes
    emotion_counts = {"no_disorder": 0, "depression": 0, "anxiety": 0}
    dimension_scores = {"no_disorder": 0, "depression": 0, "anxiety": 0}

    for _, row in rows.iterrows():
        # Contar las emociones categóricas por tipo
        for condition, emotions in emotion_weights.items():
            for emotion in row[emotion_columns]:
                if emotion in emotions:
                    weight_range = emotions[emotion]
                    weight = np.random.uniform(weight_range[0], weight_range[1])
                    emotion_counts[condition] += weight

        # Analizar dimensiones emocionales
        for emotion in row[emotion_columns]:
            if emotion in emotion_dimension_map:
                for dimension in dimensions:
                    dim_value = row[dimension]
                    dim_range = emotion_dimension_map[emotion][dimension]
                    if dim_range[0] <= dim_value <= dim_range[1]:
                        for condition in dimension_scores.keys():
                            if emotion in emotion_weights[condition]:
                                dimension_scores[condition] += 1

    # Normalizar los puntajes para evitar sesgos
    total_emotion_counts = sum(emotion_counts.values())
    total_dimension_scores = sum(dimension_scores.values())

    if total_emotion_counts > 0:
        emotion_counts = {k: v / total_emotion_counts for k, v in emotion_counts.items()}
    if total_dimension_scores > 0:
        dimension_scores = {k: v / total_dimension_scores for k, v in dimension_scores.items()}

    # Combinar los puntajes de emociones y dimensiones
    final_scores = {
        condition: emotion_counts[condition] + dimension_scores[condition]
        for condition in emotion_counts.keys()
    }

    # Debug: Imprimir los puntajes para depuración
    print(f"Emotion counts: {emotion_counts}")
    print(f"Dimension scores: {dimension_scores}")
    print(f"Final scores: {final_scores}")

    # Determinar la condición con el puntaje más alto
    return max(final_scores, key=final_scores.get)

# Cargar el CSV y predecir las condiciones por user_id
def classify_conditions_by_user(csv_path):
    """
    Clasifica a cada usuario de un CSV por su condición emocional predominante.
    """
    df = pd.read_csv(csv_path, sep=";")

    # Clasificar por user_id
    user_groups = df.groupby("user_id")
    user_conditions = user_groups.apply(determine_condition).reset_index()
    user_conditions.columns = ["user_id", "Predicted_Condition"]

    # Guardar resultados
    output_path = csv_path.replace(".csv", "_classified_by_user.csv")
    user_conditions.to_csv(output_path, index=False, sep=";")
    print(f"Archivo clasificado por usuario guardado en: {output_path}")

classify_conditions_by_user("resources/emotion_data_with_dimensions_full.csv")