"""
alignment_processor.py

Este módulo utiliza Whisper y WhisperX para transcribir y alinear segmentos de audio palabra por palabra.
Carga modelos dinámicamente según el idioma detectado y devuelve alineaciones temporales para cada palabra.

"""


from flask import jsonify
import whisper
import whisperx 

# Configura tu dispositivo (usa "cuda" si tienes GPU)
device = "cpu"

# Precarga del modelo ASR (base para más rapidez)
ASR_MODEL_NAME = "base"
print("Cargando modelo ASR: {ASR_MODEL_NAME}")
asr_model = whisper.load_model(ASR_MODEL_NAME)

# Diccionario para almacenar modelos de alineación por idioma
alignment_models_cache = {}


def compute_alignment(audio_path):
    """
    Realiza transcripción y alineación palabra a palabra del audio especificado.

    Utiliza Whisper para transcripción automática del habla (ASR) y WhisperX para alinear cada palabra con su tiempo de inicio y fin.

    Args:
        Ruta al archivo de audio.

    Returns:
        Alineamientos. Cada uno con la palabra y su tiempo de inicio y de fin.

    """
    print(f"Procesando {audio_path}...")

    audio = whisperx.load_audio(audio_path)
    result = asr_model.transcribe(audio_path, language="es")
    print("Transcripción:", result)

    lang = result["language"]
    if lang not in alignment_models_cache:
        print(f"Cragando modelo junto al idioma: {lang}")
        model_a, metadata = whisperx.load_align_model(language_code=lang, device=device)
        alignment_models_cache[lang] = (model_a, metadata)
    else:
        model_a, metadata = alignment_models_cache[lang]

    result_aligned = whisperx.align(result["segments"], model_a, metadata, audio, device=device)

    alignments = []
    for segment in result_aligned["segments"]:
        for word_info in segment["words"]:
            alignments.append({
                "word": word_info["word"],
                "start": round(word_info["start"], 2),
                "end": round(word_info["end"], 2)
            })

    print(alignments)
    return alignments