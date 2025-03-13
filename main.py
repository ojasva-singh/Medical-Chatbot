from multimodal import encode_image, llm_response
from text_to_voice import text_to_speech
from voice_to_text import record_audio, convert_audio, transcription_groq

import os
import gradio as gr
import tempfile
from dotenv import load_dotenv

# System prompt for the medical assistant
SYSTEM_PROMPT = """You are a medical assistant designed to help patients understand medical images and answer their health-related questions.

Role:
- You help patients understand their medical images and related questions.
- You provide clear, accessible explanations of what can be observed in medical imagery.

Guidelines:
- Analyze the medical image provided by the patient
- Answer questions about the image in a clear, concise and accurate manner
- Provide information in simple language that patients can understand
- Be compassionate and reassuring while maintaining medical accuracy
- When appropriate, suggest when the patient should seek further medical consultation
- Do not attempt to provide definitive diagnoses, but rather describe what can be observed in the image
- Clarify that your interpretations are for informational purposes only and not a substitute for professional medical advice"""


def process_text_query(image, text):

    # Check if image and audio are provided
    if image is None:
        return "Please upload a medical image.", None
    if not text or text.strip() == "":
        return "Please enter your question.", None
    
    try:
        temp_image_path = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False).name
        image.save(temp_image_path)
        
        # Encode the image for the vision model
        encoded_image = encode_image(temp_image_path)

        final_query = f"System: {SYSTEM_PROMPT}\n\nPatient: {text}"

        response = llm_response(encoded_image, final_query)

        audio_output = text_to_speech(response)

        os.remove(temp_image_path)

        return response, audio_output


    except Exception as e:
        return f"An error occurred: {e}", None
    

def record_live_audio():
    # Record audio from the user
    try:
        audio_path = record_audio("audio.mp3")
        transcription = transcription_groq(audio_path)
        return transcription   
    except Exception as e:  
        return f"An error occurred: {e}"

# Create the Gradio interface
with gr.Blocks(title="Medical Image Voice Assistant") as demo:
    gr.Markdown("# Medical Image Voice Assistant")
    gr.Markdown("Upload a medical image (required) and ask a question about it either by typing or using the voice recording option. The assistant will analyze the image and provide a spoken response.")
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="Upload Medical Image (Required)", type="pil")
            
            text_input = gr.Textbox(label="Type your question", placeholder="What can you tell me about this image?")
            
            with gr.Row():
                record_btn = gr.Button("Record Voice Question")
                submit_btn = gr.Button("Submit Question")
        
        with gr.Column():
            response_output = gr.Textbox(label="Assistant's Response", lines=8)
            audio_output = gr.Audio(label="Spoken Response")
    
    # Set up event handlers
    record_btn.click(
        fn=record_live_audio,
        inputs=None,
        outputs=text_input
    )
    
    submit_btn.click(
        fn=process_text_query,
        inputs=[image_input, text_input],
        outputs=[response_output, audio_output]
    )
    
    # Add examples
    gr.Examples(
        examples=[
            ["example_images/xray.jpg", "What does this X-ray show?"],
            ["example_images/mri.jpg", "Is there anything concerning in this MRI?"],
            ["example_images/ultrasound.jpg", "Can you explain what I'm seeing in this ultrasound?"]
        ],
        inputs=[image_input, text_input]
    )

if __name__ == "__main__":
    demo.launch(share=True)  # Set share=True to create a shareable link