import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import os
from dotenv import load_dotenv
from groq import Groq


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


def convert_audio(file_path):
    """ Function to convert an audio file to text using the Google Web Speech API"""

    recognizer = sr.Recognizer()

    #Load the audio file
    audio_file = sr.AudioFile(file_path)

    with audio_file as source:
        audio_data = recognizer.record(source)

    logging.info("Converting audio to text...")
    try:
        text = recognizer.recognize_google(audio_data)
        logging.info(f"Text: {text}")
        return text
    except sr.UnknownValueError:
        logging.error("Google Web Speech API could not understand the audio")
    except sr.RequestError:
        logging.error("Could not request results from Google Web Speech API")


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_path = "audio.mp3"
# record_audio(file_path=file_path)


def transcription_groq(file_path):
    """ Function to convert an audio file to text using the Groq API"""
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    stt_model = "whisper-large-v3"  
    client = Groq(api_key=GROQ_API_KEY)
    audio_file = open(file_path, "rb")
    transcript = client.audio.transcriptions.create(model = stt_model, file=audio_file, language="en")
    return transcript.text