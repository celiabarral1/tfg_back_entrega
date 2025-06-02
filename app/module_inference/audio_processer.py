"""
audio_processer.py

Módulo para procesar archivos de audio (.wav) y realizar inferencia emocional utilizando diferentes tipos de modelos.
También incluye utilidades para guardar archivos de audio y listar modelos disponibles.
"""

import os
from app.module_inference.infere_emotion.predict_emotions_folderwavs import interfere_emotion
from models.models import load_model
from features_extraction.extract_features_w2v2 import Feature_Extractor as fe_w2v2
from features_extraction.extract_features_ours import Feature_Extractor as fe_ours
from features_extraction.extract_features_pretrained import Feature_Extractor as fe_pre

from app.model.audio_convert import AudioConvert

# volcado-output.csv almacena todos los datos obtenidos de procesar emocionalmente audios
# devuelve para el audio sus datos emocionales
def get_emotions_audio(model_folder,model_name,wav_path):
    """
    Recibe la ruta de un audio y aplica el modelo de inteligencia emocional.

    Returns
        Análisis emocional en forma de lista.
    """
    dataset_name = model_name.split("_")[-1].split('.')[0]
    csv_folder = './data/output-predict-emotions/'
    csvfile = os.path.join(csv_folder, 'volcado-output.csv')

    # Crear carpetas si no existen
    os.makedirs(csv_folder, exist_ok=True)
    
    model, model_type = load_model(model_folder, model_name)
    if model_type == 'pretrained':
        feature_loader = fe_pre()
    elif model_type == 'w2v2':
        feature_loader = fe_w2v2()
    else:
        feature_loader = fe_ours(model['mfcc'][0], model['mfcc'][1])


    return interfere_emotion(dataset_name,wav_path,feature_loader,model,
            model_type,csvfile,worker_id=None)


def convert_audio_to_wav(audio):
    """
    Convierte y guarda un archivo recibido en local.
    """
    if not audio.filename.lower().endswith('.wav'):
        raise ValueError("Debe ser tipo .wav")

    # Ruta de la carpeta donde se guardarán los archivos 
    save_folder = os.path.join(os.getcwd(), 'resources/audios')
    audio_converter = AudioConvert(save_folder)

    # Leer y guardar el archivo .wav
    wav_data = audio.read()
    wav_audioname = audio.filename
    wav_path = audio_converter.save_wav_audio(wav_data, wav_audioname)

    if not wav_path:
        raise RuntimeError(f"Error converting the audio {audio.filename}")

    return wav_path


def get_all_model_files():
    """
    Devuelve una lista de modelos de inferencia disponibles en formato .pkl.
    """
    models_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'models'))
    print(models_dir)
    try:
        return [
            {
                "label": os.path.splitext(filename)[0].replace('_', ' ').title(),
                "value": filename
            }
            for filename in os.listdir(models_dir)
            if filename.endswith('.pkl')
        ]
    except FileNotFoundError:
        return []
