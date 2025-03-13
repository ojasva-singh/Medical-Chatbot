import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def record_audio(file_path, timeout=20, phrase_time_limit = None):
    """ Function to record audio from the microphone and save it as an mp3 file"""

    recognizer = sr.Recognizer()

    try: 
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")

            #Record the audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete. Saving the audio file...")

            #Convert the audio data to mp3 format
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")

            logging.info(f"Audio file saved at {file_path}")
    
    except sr.WaitTimeoutError:
        logging.error("Timeout error. Recording stopped.")

record_audio(file_path="audio.mp3")

