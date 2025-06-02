import pytest
import os
from unittest.mock import patch, MagicMock
from app.module_inference.audio_processer import convert_audio_to_wav, get_emotions_audio
from app.model.audio_convert import AudioConvert
from force_alignment_processor import compute_alignments, process, transcribe_audio

@pytest.fixture
def mock_audio():
    mock = MagicMock()
    mock.filename = "audio.wav"
    mock.read.return_value = b"text"
    return mock


@patch.object(AudioConvert, 'save_wav_audio', return_value="resources/audios/audio.wav")
def test_convert_audio_to_wav(mock_save_wav_audio, mock_audio):
    wav_path = convert_audio_to_wav(mock_audio)
    assert wav_path == "resources/audios/audio.wav"
    mock_save_wav_audio.assert_called_once()


@patch("app.module_inference.audio_processer.load_model", return_value=(MagicMock(), "pretrained"))
@patch("app.module_inference.audio_processer.interfere_emotion", return_value={"happiness": 0.7, "sadness": 0.2})
def test_get_emotions_audio(mock_interfere_emotion, mock_load_model):
    emotions = get_emotions_audio("models/", "model_ours_MIXED.pkl", "test.wav")
    assert "happiness" in emotions
    assert emotions["happiness"] == 0.7
    mock_interfere_emotion.assert_called_once()

@patch("force_alignment_processor.whisper.load_model")
def test_transcribe_audio(mock_whisper):
    mock_model = MagicMock()
    mock_whisper.return_value = mock_model
    mock_model.transcribe.return_value = {"text": "Prueba audio"}

    transcription = transcribe_audio("audio.wav")
    assert transcription == "Prueba audio"
    mock_model.transcribe.assert_called_once_with("audio.wav", language="es")


def test_normalize():
    text = "¡Hola, ¿cómo estás?"
    expected = "hola como estas"
    assert process(text) == expected


def test_transform_number_to_text():
    assert process("Tengo 3 manzanas") == "tengo tres manzanas"
    assert process("5.99") == "cinco coma noventa y nueve"

