import speech_recognition as sr
from pydub import AudioSegment
import os
import time
import yt_dlp

def descargar_audio_youtube(url):
    """
    Descarga el audio de un video de YouTube usando yt-dlp.

    :param url: URL del video de YouTube.
    :return: Ruta del archivo de audio descargado o None si hay un error.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'youtube_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        print("🔄 Descargando audio de YouTube...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "youtube_audio.mp3"
    except Exception as e:
        print(f"❌ Error al descargar el audio: {e}")
        return None

def comprimir_audio(audio_path):
    """
    Comprime el archivo de audio para facilitar la transcripción.

    :param audio_path: Ruta del archivo de audio original.
    :return: Ruta del archivo de audio comprimido.
    """
    print("🔊 Compresión de audio en marcha... 🚀")
    audio = AudioSegment.from_file(audio_path)

    # Reduciendo la calidad y el número de canales (mono)
    compressed_audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    compressed_audio.export("audio_temp.wav", format="wav")
    
    return "audio_temp.wav"

def transcribir_audio_google(audio_path):
    """
    Transcribe el audio utilizando Google Speech Recognition.

    :param audio_path: Ruta del archivo de audio a transcribir.
    :return: Texto transcrito o mensaje de error.
    """
    recognizer = sr.Recognizer()

    # Llamamos a la función de compresión antes de transcribir
    audio_path = comprimir_audio(audio_path)

    with sr.AudioFile(audio_path) as source:
        print("📝 Transcribiendo el audio...")

        # Lee el audio para la transcripción
        audio_data = recognizer.record(source)

        while True:  # Espera indefinida hasta que se complete la transcripción
            try:
                text = recognizer.recognize_google(audio_data, language="es-ES")
                return separar_en_parrafos(text)
            except sr.UnknownValueError:
                return "🤔 No entendí bien el audio, ¿quizás puedes intentar con otro?"
            except sr.RequestError as e:
                print(f"⚠️ Error de conexión: {e}. Reintentando...")
                time.sleep(5)  # Esperar 5 segundos antes de reintentar
            except Exception as e:
                return f"❌ Error inesperado: {e}"

def separar_en_parrafos(texto):
    """
    Separa el texto en párrafos basándose en ciertas reglas.

    :param texto: Texto transcrito.
    :return: Texto con párrafos separados.
    """
    # Aquí definimos criterios simples para separar párrafos
    # Por ejemplo, separando después de frases que terminan en punto o nuevas líneas
    oraciones = texto.split('. ')
    parrafos = []
    parrafo_actual = ""

    for oracion in oraciones:
        parrafo_actual += oracion.strip() + '. '
        
        # Supongamos que un nuevo párrafo empieza si encontramos una oración larga (más de 15 palabras)
        if len(oracion.split()) > 15:
            parrafos.append(parrafo_actual.strip())
            parrafo_actual = ""

    if parrafo_actual:
        parrafos.append(parrafo_actual.strip())

    return '\n\n'.join(parrafos)

def chatbot():
    """
    Interfaz de usuario en consola para interactuar con el chatbot.
    Permite al usuario ingresar enlaces de YouTube para transcribir el audio.
    """
    print("🌟 ¡Hola! Soy tu amigo transcriptor 😊.")
    print("🎥 ¿Tienes algún video de YouTube que quieras transcribir?")
    
    while True:
        url = input("🔗 Pega aquí el enlace de YouTube (o escribe 'salir' para terminar): ")
        
        if url.lower() == "salir":
            print("👋 ¡Nos vemos! Cualquier cosa, aquí estaré para ayudarte.")
            break

        # Descargar y transcribir
        audio_path = descargar_audio_youtube(url)
        if audio_path:
            print("⌛ Esto podría tardar un poco... ¡voy a hacer lo mío!")
            time.sleep(2)
            transcripcion = transcribir_audio_google(audio_path)
            print("\n--- Transcripción ---")
            print(transcripcion)
            print("--- Fin de la transcripción ---\n")

            # Diálogo amistoso después de la transcripción
            print("¿Qué te ha parecido? 😊 ¡Puedo seguir transcribiendo más cosas si quieres!")

            # Eliminar archivo descargado
            os.remove(audio_path)

# Ejecutar el chatbot
if __name__ == "__main__":
    chatbot()
