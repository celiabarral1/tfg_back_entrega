import pytest
import pandas as pd
import numpy as np
from app.module_analysis.analysis_processor import determine_condition

@pytest.fixture
def mock_data():
    data = [
        {"user_id": 1, "Emotion_1_label": "happiness", "Emotion_2_label": "neutral", "Emotion_3_label": "happiness", "arousal": 0.6, "valence": 0.8, "dominance": 0.7},
        {"user_id": 2, "Emotion_1_label": "sadness", "Emotion_2_label": "disgust", "Emotion_3_label": "sadness", "arousal": 0.2, "valence": -0.8, "dominance": -0.5},
        {"user_id": 3, "Emotion_1_label": "fear", "Emotion_2_label": "sadness", "Emotion_3_label": "fear", "arousal": 0.9, "valence": -0.9, "dominance": -0.8},
    ]
    return pd.DataFrame(data)

# Trabajador sin trastorno
def test__no_disorder(mock_data):
    user_data = mock_data[mock_data["user_id"] == 1]
    predicted_condition = determine_condition(user_data)
    assert predicted_condition == "no_disorder"

# Trabajador con depresión
def test_depression(mock_data):
    user_data = mock_data[mock_data["user_id"] == 2]
    predicted_condition = determine_condition(user_data)
    assert predicted_condition == "depression"

# Trabajador con ansiedad
def test_anxiety(mock_data):
    user_data = mock_data[mock_data["user_id"] == 3]
    predicted_condition = determine_condition(user_data)
    assert predicted_condition == "anxiety"


def test_empty():
    empty_df = pd.DataFrame(columns=["user_id", "Emotion_1_label", "Emotion_2_label", "Emotion_3_label", "arousal", "valence", "dominance"])
    result = determine_condition(empty_df)
    assert result in {"no_disorder", "depression", "anxiety"} 
