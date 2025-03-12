# Medical Chatbot

The purpose of this chatbot is to use multimodal llms and then take the help of AI to answer some medical questions by providing some text and images for relevance.

## Tools and Technologies

- Groq for AI inference
- OpenAI Whisper (STT)
- LLAMA 3 Vision
- gTTS and ElevenLabs (TTS)
- Gradio for UI
- Python 3.9


## Workflow

1. Patient will upload the image and ask the question to the model
2. The query will be given to the LLM
3. Audio will be given as output

## Backend

1. The image is passed to the vision model.
2. The query asked by the patient is converted to text by using Whisper.
3. The image and text query is then given to the LLM to reason and give an answer.
4. The LLM answer is then converted to speech by using ElevenLabs and then read aloud by the system.


### (For requirements check the requirements.txt file)
