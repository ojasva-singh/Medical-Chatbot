import os
from elevenlabs import ElevenLabs
from elevenlabs import play
from dotenv import load_dotenv
import elevenlabs

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def text_to_speech(input_text, output_filepath):
    """ Function to convert text to speech using ElevenLabs API"""
    client = ElevenLabs(
        api_key=ELEVENLABS_API_KEY
    )

    audio = client.generate(
        text = input_text,
        voice = "Sarah",
        output_format = "mp3_22050_32",
        model = "eleven_turbo_v2",
    )

    elevenlabs.save(audio, output_filepath)
    play(audio)

text = "Hi my name is ojasva singh and this is a demo of text to speech conversion"
text_to_speech(input_text = text, output_filepath = "output.mp3")