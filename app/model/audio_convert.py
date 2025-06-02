from pydub import AudioSegment
import io, os

AudioSegment.ffmpeg = "C:\\Program Files\\ffmpeg-7.1-full_build\\bin\\ffmpeg.exe"


class AudioConvert:
    def __init__(self, output_folder):
        self.output_folder = output_folder  # Carpeta donde se guardarán los archivos .wav
        os.makedirs(self.output_folder, exist_ok=True)

    def convert_webm_to_wav(self, webm_data, wav_filename):
        try:
            # Convertir el archivo webm en memoria
            webm_io = io.BytesIO(webm_data)
            audio = AudioSegment.from_file(webm_io, format="webm")

            # Ruta de salida para el archivo wav
            wav_path = os.path.join(self.output_folder, wav_filename)

            # Exportar como .wav en memoria y guardar en el disco
            audio.export(wav_path, format="wav")
            print(f"Archivo convertido y guardado como WAV: {wav_path}")
            return wav_path
        except Exception as e:
            print(f"Error al convertir el archivo a WAV: {e}")
            return None
        
    def save_wav_audio(self, wav_data, wav_filename):
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
