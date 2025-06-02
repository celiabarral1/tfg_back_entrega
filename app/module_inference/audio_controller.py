"""
audio_controller.py

Módulo Flask que gestiona endpoints relacionados con el procesamiento de audio:
- Transcripción y alineación de palabras usando Whisper.
- Detección de emociones a partir del archivo de audio.
- Consulta de modelos de inferencia y configuración actual.

Blueprint:
    audio_bp: Agrupa las rutas bajo el prefijo /audio.

"""

import os
from app.module_inference.audio_processer import convert_audio_to_wav, get_emotions_audio, get_all_model_files
from flask import Blueprint, current_app, jsonify, request

from app.model.audio_convert import AudioConvert
from force_alignment_processor import  compute_alignments, process, transcribe_audio
# from force_alignment_processor import compute_alignment_new

audio_bp = Blueprint('audios', __name__)

# Enpoint para recibir un audio, almacenarlo y procesar sus emociones y registrarlas
@audio_bp.route('/audio/getData', methods=['POST'])
def get_data_audio():
    """
    Endpoint que procesa un archivo .wav y produce un análisis emocional.

    Args
        Audio formato .wav.

    Returns
        Objetivo JSON con:
        - Emociones categóricas y dimensionales predominantes.
        - Forced alignment.
    """
    audio = request.files.get('audioFile')  

    if not audio:
        return jsonify({'message': 'No se encontró el audio'}), 400
    
    try:
        wav_path = convert_audio_to_wav(audio)
        # Transcribir el audio usando Whisper
        transcript = transcribe_audio(wav_path)

        normalized_text = process(transcript)

         # Calcular alineaciones 
        alignments = compute_alignments(wav_path, normalized_text)
        # alignments = compute_alignment_new(wav_path)

        # Procesar el audio y obtener emociones
        model_name = 'model_ours_MIXED.pkl'
        model_folder = 'data/models/'

        emotions = get_emotions_audio(model_folder,model_name,wav_path)

        # Retornar la respuesta con los datos procesados
        return jsonify({
            'message': f'Audio {audio.filename} processed successfully',
            'transcription': transcript,
            'normalized': normalized_text,
            'alignments': alignments,
            # 'number': number_text,
            'emotions': emotions
        }), 200

    except Exception as e:
        print(f"Error processing the audio {audio.filename}: {e}")
        return jsonify({'message': f'Error processing the audio {audio.filename}'}), 500
    

# Enpoint para recuperar los modelos disponibles de inferencia
@audio_bp.route('/audio/getAvalaibleModels', methods=['GET'])
def get_models():
    model_files = get_all_model_files()
    """
    Devuelve una lista con los nombres de los modelos de inferencia disponibles .pkl
    """
    return jsonify(model_files)


# Enpoint para obtener el valor de silencio entre palabras
@audio_bp.route('/audio/getInferenceInterval', methods=['GET'])
def get_inference_interval():
    """
    Devuelve el valo configurado como intervalo de silencio entte grabaciones
    """
     # Accede directamente a INFERENCE.silence_interval
    silence_interval = current_app.config.get("INFERENCE", {}).get("silence_interval", None)
    print(silence_interval)

    return jsonify({"silence_interval": silence_interval}), 200

 