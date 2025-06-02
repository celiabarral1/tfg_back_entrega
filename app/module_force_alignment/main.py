"""
main.py

Servidor Flask que agrupa los endpoints relacionados con el forced alignment
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from force_alignment_whisperx import compute_alignment
import whisper
import whisperx  

app = Flask(__name__)
CORS(app) 


class AudioConvert:
    """
    Clase encargada de guardar archivos de audio .wav en una carpeta específica.
    """
    def __init__(self, output_folder):
        self.output_folder = output_folder  # Carpeta donde se guardarán los archivos .wav
        os.makedirs(self.output_folder, exist_ok=True)

        
    def save_wav_audio(self, wav_data, wav_filename):
        """
        Guarda un archivo de audio como .wav en disco.
        """
        try:
            # Ruta de salida para el archivo wav
            wav_path = os.path.join(self.output_folder, wav_filename)

            # Guardar el archivo WAV directamente en el disco
            with open(wav_path, 'wb') as file:
                file.write(wav_data)

            print(f"Archivo guardado como WAV: {wav_path}")
            return wav_path
        except Exception as e:
            print(f"Error al guardar el archivo WAV: {e}")
            return None


def convert_audio_to_wav(audio):
    """
    Valida y guarda un archivo de audio recibido como archivo .wav.
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

@app.route("/getForcedAlignment", methods=['POST'])
def get_forced_alignment():
    """
    Endpoint que procesa el forced alignment de un audio.

    Input:
        Audio en formato .wav

    Returns:
        JSON con el alineamiento de la transcripción con el audio o error.
    """
    audio = request.files.get("audioFile")
    if not audio:
        return jsonify({"error": "No audio file received"}), 400

    try:
        wav_path = convert_audio_to_wav(audio)
        alignments = compute_alignment(wav_path)
        # os.remove(wav_path)  # Limpieza del archivo temporal
        return jsonify(alignments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
