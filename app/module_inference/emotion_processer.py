import os
from infere_emotion.predict_emotions_folderwavs import test_folder
from models.models import Pretrained_Model_Dimensional
import numpy as np
from time import sleep

from utils.utils import decode_label

"""
emotion_processor.py

Clase que procesa archivos de audio y extraee tanto emociones categóricas como dimensionales a partir de modelos preentrenados.
"""
class EmotionProcessor:
    def __init__(self, model, feature_loader, dataset_name):
        self.model = model
        self.feature_loader = feature_loader
        self.dataset_name = dataset_name

    def get_emotions(self, features, mode="hard"):
        """
        Realiza inferencia emocional.
        """
        predictions = []
        if mode == "hard":
            if isinstance(self.model, dict):
                features = self.model['scaler'].transform(features)
                for model in self.model['models']:
                    predictions.append(model.predict(features))
                predictions = np.array(predictions, dtype=object)
                unique_elements, counts = np.unique(predictions, return_counts=True)
                return unique_elements[np.argmax(counts)].item()
            else:
                return int(self.model.predict(features))
        elif mode == "soft":
            if isinstance(self.model, dict):
                features = self.model['scaler'].transform(features)
                for model in self.model['models']:
                    predictions.append(model.predict_proba(features))
                return np.mean(predictions, axis=0), np.std(predictions, axis=0)
            else:
                return self.model.predict_proba(features), [[0]]

    def process_audio(self, audio_file):
        """
        Procesa un archivo de audio .wav para extraer emociones categóricas y dimensionales.
        """
        features = self.feature_loader.get_features(audio_file)
        por_accuracy, std = self.get_emotions(features, "soft")
        label = self.get_emotions(features, "hard")
        dimensional_values = Pretrained_Model_Dimensional().predict(audio_file)
        return {
            "emocategoric": [{"emo": decode_label(i, self.dataset_name), "prob": por_accuracy[i]} for i in np.argsort(por_accuracy)[-3:][::-1]],
            "emodimensional": {
                "valence": float(dimensional_values[0]),
                "arousal": float(dimensional_values[1]),
                "dominance": float(dimensional_values[2]),
            },
        }
