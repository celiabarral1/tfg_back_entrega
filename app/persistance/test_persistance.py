import pytest
import pandas as pd
import tempfile
import os
from datetime import datetime

from persistance import RecordDataCSV


@pytest.fixture
def sample_csv():
    """Crea un archivo CSV temporal con datos de prueba."""
    data = """user_id;timestamp;Emotion_1_label;Emotion_2_label;Emotion_3_label
1;1706640000;happy;sad;angry 
1;1706726400;neutral;happy;sad
2;1706726400;angry;neutral;happy
2;1706812800;sad;angry;neutral
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_file.write(data.encode('utf-8'))
    temp_file.close()
    return temp_file.name

@pytest.fixture
def record_data_instance(sample_csv):
    """Crea una instancia de RecordDataCSV con el archivo de prueba."""
    return RecordDataCSV(file_path=sample_csv)

def test_load_records(record_data_instance):
    """Verifica que los datos se cargan correctamente."""
    assert len(record_data_instance.data) == 4  # Debe haber 4 registros en el archivo

def test_filter_records_by_user_date(record_data_instance):
    """Prueba la función de filtrado por usuario y fecha."""
    start_date = datetime(2024, 1, 30)
    end_date = datetime(2024, 2, 1)

    user_1_records = record_data_instance.filter_records_by_user_date(1, start_date, end_date)
    assert len(user_1_records) == 2  # Usuario 1 tiene 2 registros en este rango

def test_filter_by_date_and_shift(record_data_instance):
    """Prueba el filtrado por fecha y turno."""
    start_date = datetime(2024, 1, 30)
    end_date = datetime(2024, 2, 2)

    morning_records = record_data_instance.filter_by_date_and_shift(start_date, end_date, "mañana")
    assert isinstance(morning_records, list)  # Debe retornar una lista

def test_get_emotions(record_data_instance):
    """Prueba la extracción de emociones únicas."""
    emotions = record_data_instance.get_emotions()
    expected_emotions = ["angry", "happy", "neutral", "sad"]
    assert set(emotions) == set(expected_emotions)  # Las emociones deben coincidir

@pytest.fixture(scope="function", autouse=True)
def cleanup(sample_csv):
    """Elimina el archivo temporal después de ejecutar las pruebas."""
    yield
    os.remove(sample_csv)
