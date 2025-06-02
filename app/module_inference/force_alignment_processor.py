import os
import subprocess
from flask import jsonify
import torch
import whisper
from unidecode import unidecode
import re
from num2words import num2words
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import subprocess
import torchaudio
import torch
from torchaudio.pipelines import Wav2Vec2FABundle
import torchaudio.transforms as T
from torchaudio.models import wav2vec2_model
from torchaudio.pipelines import Wav2Vec2ASRBundle
import numpy as np
# import whisperx


# Cargar el tokenizador (convierte el texto en tokens)
# y modelo BERT preentrenado
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertModel.from_pretrained('bert-base-uncased')

# Configurar el pipeline de alineamiento
# Cargar el modelo preentrenado en español

# model_name = "facebook/wav2vec2-large-xlsr-53-spanish"
# model = Wav2Vec2ForCTC.from_pretrained(model_name)
# processor = Wav2Vec2Processor.from_pretrained(model_name)

# Load model directly
from transformers import AutoProcessor, AutoModelForCTC
import wave


processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-xlsr-53-spanish")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-xlsr-53-spanish")

def transcribe_audio(audio_path):
    # Cargar el modelo Whisper
    model = whisper.load_model("base")  # Puedes usar otros modelos como "small", "medium", "large"
    
    # Transcribir el audio
    result = model.transcribe(audio_path, language="es")  # Especifica el idioma
    
    # Obtener la transcripción
    transcription = result["text"]
    return transcription


# Normaliza el texto
def normalize(transcription): 
    # Pasar números a texto
    transcription = transform_number_to_text(transcription)
    # Eliminar acentos y normalizar
    normalized = unidecode(transcription)
    # Eliminar signos de puntuación
    # normalized = normalized.translate(str.maketrans('', '', string.punctuation))  -> ¿Eliminar signos de puntuación?

    # Sin espacios y en minúsculas
    normalized = ' '.join(normalized.lower().split())
    # Eliminar caracteres no alfabéticos 
    normalized = re.sub(r'[^a-záéíóúüñ0-9\s]', '', normalized)
    # Eliminar espacios adicionales
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized

# Transforma texto 
def transform_number_to_text(text):
    # Expresión regular para encontrar números (enteros y decimales)
    patron = r'\d+\.\d+|\d+'
    
    def replace_number(match):
        numero = match.group(0)
        if '.' in numero:
            entero, decimal = numero.split('.')
            decimal_int = int(decimal)  # Convertir la parte decimal a número entero
            
            if len(decimal) > 1:
                decimal_en_palabras = num2words(decimal_int, lang='es')
            else:
                # Si es un solo dígito, se pronuncia por separado
                decimal_en_palabras = " ".join([num2words(int(d), lang='es') for d in decimal])
            
            return f"{num2words(int(entero), lang='es')} coma {decimal_en_palabras}"
        else:
            return num2words(int(numero), lang='es')
        
    return re.sub(patron, replace_number, text)



# Función principal para normalizar y convertir los números
def process(text):
    texto_normalizado = normalize(text)
    # final_text = transform_number_to_text(text)
    return texto_normalizado


def compute_alignments(audio_path, transcript):
    # Cargar el audio
    waveform, sample_rate = torchaudio.load(audio_path)
    
    # Resamplear si es necesario
    if sample_rate != processor.feature_extractor.sampling_rate:
        resampler = torchaudio.transforms.Resample(
            orig_freq=sample_rate, new_freq=processor.feature_extractor.sampling_rate
        )
        waveform = resampler(waveform)
    
    # Preprocesar el audio
    inputs = processor(
        waveform.squeeze().numpy(),
        return_tensors="pt",
        sampling_rate=processor.feature_extractor.sampling_rate,
        padding=True,
    )
    
        # Comparar transcripción real con predicha para alineamientos (por palabras)
    alignments = []
    words_in_transcript = transcript.split()  # Dividir la transcripción real en palabras

    if not words_in_transcript:
        raise ValueError("La transcripción está vacía. No se puede procesar el audio.")
    
    print(f"Transcripción real: {words_in_transcript}")

    # Verificar las longitudes
    num_tokens = len(words_in_transcript)  # Número de palabras en la transcripción
    num_frames = waveform.size(1)  # Número de frames en el audio
    print(f"Tokens: {num_tokens}, Frames: {num_frames}")

    # Obtener las posiciones de los tokens en el audio
    token_positions = []
    for i in range(num_tokens):
        token_start_frame = int(i * (num_frames / num_tokens))
        token_end_frame = int((i + 1) * (num_frames / num_tokens))

        # Convertir frames a tiempo
        start_time = token_start_frame / sample_rate
        end_time = token_end_frame / sample_rate

        token_positions.append(
            (words_in_transcript[i], start_time, end_time)
        )

    # Alinear tokens con la transcripción real
    for i, (token, start_time, end_time) in enumerate(token_positions):
        if i < len(transcript.split()):
            alignments.append((transcript.split()[i], start_time, end_time))
        else:
            print(f"Warning: Token {token} could not be aligned.")

    return alignments

def compute_alignments(audio_path, normalized_text):
    # Cargar el modelo preentrenado en español
    model_name = "jonatasgrosman/wav2vec2-large-xlsr-53-spanish"
    processor = Wav2Vec2Processor.from_pretrained(model_name)
    model = Wav2Vec2ForCTC.from_pretrained(model_name).eval()

    # Cargar el audio
    waveform, sample_rate = torchaudio.load(audio_path)

    # Reescalar el audio al sample rate del modelo (si es necesario)
    target_sample_rate = processor.feature_extractor.sampling_rate
    if sample_rate != target_sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        waveform = resampler(waveform)

    # Preparar el audio para el modelo
    input_values = processor.feature_extractor(waveform.squeeze(0).numpy(), sampling_rate=target_sample_rate, return_tensors="pt").input_values

    # Procesar el texto normalizado y convertirlo en etiquetas (token IDs)
    with processor.as_target_processor():
        labels = processor.tokenizer(normalized_text, return_tensors="pt").input_ids.squeeze()

    # Ejecutar el modelo para obtener predicciones
    with torch.no_grad():
        logits = model(input_values).logits

    # Decodificar alineaciones forzadas (implementación personalizada para alineación)
    alignments = []  
    for i, token_id in enumerate(labels):
        token = processor.tokenizer.decode([token_id])
        start_time = i * (len(waveform.squeeze(0)) / len(labels)) / target_sample_rate
        end_time = start_time + (len(waveform.squeeze(0)) / len(labels)) / target_sample_rate
        alignments.append({
            "word": token,
            "start": start_time,
            "end": end_time
        })

    print(alignments)
    return alignments


# import whisperx 

# def compute_alignment_new(audio_path):
#     # WhisperX model sizes
#     models_asr = ["base", "small", "medium", "large"]
#     device = "cpu"  # or "cuda" if using GPU

#     for model_name in ['turbo']:
#             print(f"🔁 Processing {audio_path} with model: {model_name}")
#             # Load model
#             model = whisper.load_model(model_name)
#       # Load and transcribe audio
#             audio = whisperx.load_audio(audio_path)
#             #audio = whisper.load_audio(audio_path)
#             result = model.transcribe(audio_path, language="es")
 
#             # Load alignment model
#             model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
 
#             # Align transcription
#             result_aligned = whisperx.align(result["segments"], model_a, metadata, audio, device=device)

#             alignments = []  
#     # Write each word and its timestamps
#             for segment in result_aligned["segments"]:    
#                 for word_info in segment["words"]:
#                     alignments.append({
#                         "word": word_info["word"],
#                         "start": round(word_info["start"], 2),
#                         "end": round(word_info["end"], 2)
#                     })

#     print(alignments)
#     return alignments

# def compute_alignments(audio_path, transcript):
#     import torchaudio
#     from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
#     import torch

#     # Cargar el archivo de audio
#     waveform, sample_rate = torchaudio.load(audio_path)

#     # Convertir la tasa de muestreo a 16000 Hz si es necesario
#     if sample_rate != 16000:
#         waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)
#         sample_rate = 16000

#     # Si el audio tiene múltiples canales, convertir a mono
#     if waveform.shape[0] > 1:
#         waveform = waveform.mean(dim=0)  # Convertir a mono

#    # Añadir dimensión de batch_size
#     # Añadir dimensión de batch_size
#     waveform = waveform.unsqueeze(0)  # [batch_size, seq_len]

#     # Verificar la forma del tensor
#     print(f"Forma final del tensor: {waveform.shape}")

#     # Cargar el modelo y el procesador preentrenado en español
#     processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")
#     model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish").to("cpu")

#     # Transcripción normalizada
#     transcript = transcript.split()
#     print(f"Transcripción: {transcript}")

#     # Generar emisiones
#     inputs = processor(waveform, sampling_rate=sample_rate, return_tensors="pt", padding=True)
#     input_values = inputs.input_values  # No aplicar squeeze aún
#     print(f"Forma de input_values: {input_values.shape}")

#     # Comprobar si es necesario aplicar squeeze
#     if input_values.dim() == 4:  # Si tiene una dimensión extra de tamaño 1
#         input_values = input_values.squeeze(1)  # Eliminar la dimensión de tamaño 1 en el batch_size
#         print(f"Forma de input_values después de squeeze: {input_values.shape}")
#     else:
#         print("No es necesario aplicar squeeze")
#     # Procesar logits
#     with torch.no_grad():
#         print("Procesando logits")
#         print(f"Forma de input_values antes de pasar al modelo: {input_values.shape}")
        
#         # Aplicar squeeze para eliminar la dimensión extra de tamaño 1 en la segunda posición
#         input_values = input_values.squeeze(1)  # Asegúrate de asignar el resultado a input_values
#         print(f"Forma de input_values después de squeeze: {input_values.shape}")
        
#         # Pasar los datos al modelo
#         logits = model(input_values).logits
#         print(f"Forma de logits después de procesar: {logits.shape}")

#     # Asegurarse de que logits tenga la forma correcta (2D o 3D)
#     if logits.dim() == 4:  # Si tiene 4 dimensiones, eliminar una dimensión extra
#         logits = logits.squeeze(1)  # Eliminar la dimensión extra
#         print(f"Forma de logits después de squeeze: {logits.shape}")

#     print('pre alignments')
#     # Realizar el alineamiento
#     emissions = torch.nn.functional.log_softmax(logits, dim=-1)
#     alignments = torchaudio.functional.forced_align(
#         emissions.squeeze(0),  # Eliminar batch dimension si es necesario
#         transcript,
#         processor.tokenizer.get_vocab()
#     )

#     # Formatear los resultados
#     results = []
#     for alignment in alignments:
#         results.append({
#             "word": alignment.word,
#             "start": alignment.start,
#             "end": alignment.end
#         })

#     return results

