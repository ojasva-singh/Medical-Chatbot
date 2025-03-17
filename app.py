import streamlit as st
import os
import tempfile
from PIL import Image
from dotenv import load_dotenv
import time

# Import your existing backend functions
from multimodal import encode_image, llm_response
from text_to_voice import text_to_speech
from voice_to_text import record_audio, convert_audio, transcription_groq

# Load environment variables
load_dotenv()

# System prompt for the medical assistant 
SYSTEM_PROMPT = """You are a medical assistant designed to help patients understand medical images and answer their health-related questions.

Role:
- You help patients understand their medical images and provide preliminary assessments.
- You provide clear, accessible explanations of what can be observed in medical imagery.
- You always offer professional recommendations after your assessment.

Guidelines:
- Always analyze the medical image provided by the patient
- First, provide a clear preliminary assessment of what you observe in the image
- Describe visible patterns, structures, or abnormalities in simple terms
- Use medical terminology when necessary but explain it in patient-friendly language
- When providing your assessment, be honest about what is visible while avoiding absolute certainty
- Always follow your assessment with specific recommendations for professional follow-up
- Suggest the appropriate type of specialist the patient should consult based on your observations
- Mention the urgency level for seeking professional care (routine, soon, urgent)
- Be compassionate and reassuring while maintaining medical accuracy

Assessment Structure:
- Begin with "Based on this image, I observe..." followed by your detailed observations
- Then state "This may indicate..." with possible interpretations
- Always conclude with "I recommend..." followed by professional consultation advice

Output Format:
- Always include both an assessment and professional recommendation
- Structure your response in 2-3 sentences for the assessment
- Add 1-2 sentences for professional recommendations
- Maximum total length of 4-5 sentences
- Use clear, direct language with appropriate medical terminology explained

Important Note:
- Always clarify that your assessment is preliminary, based only on the image
- Emphasize that only a qualified healthcare provider can provide a definitive diagnosis
- Make it clear that your interpretations are for informational purposes only
"""

# Initialize session state variables if they don't exist
if 'response' not in st.session_state:
    st.session_state.response = ""
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'voice_transcription' not in st.session_state:
    st.session_state.voice_transcription = None

def process_query():
    """Process the user's query with the uploaded image"""
    if st.session_state.processed_image is None:
        st.error("Please upload a medical image first.")
        return
    
    if not st.session_state.question or st.session_state.question.strip() == "":
        st.error("Please enter your question.")
        return
    
    with st.spinner("Analyzing image and generating response..."):
        try:
            # Save the image to a temporary file
            temp_image_path = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False).name
            
            # Convert the image to RGB mode before saving as JPEG
            # This fixes the "cannot write mode P as JPEG" error
            rgb_image = st.session_state.processed_image.convert('RGB')
            rgb_image.save(temp_image_path)
            
            # Log information for debugging
            debug_info = f"Image saved to {temp_image_path}, size: {rgb_image.size}"
            
            # Encode the image for the vision model
            encoded_image = encode_image(temp_image_path)
            
            # Format the query with system prompt
            final_query = f"""System: {SYSTEM_PROMPT}

Patient: {st.session_state.question}

Please analyze the medical image and respond to the patient's question."""

            # Get response from LLM with better error handling
            try:
                # Log the query for debugging
                debug_info += f"\nQuery length: {len(final_query)} chars"
                
                # Call the LLM
                response = llm_response(final_query, encoded_image)
                
                # Check if response is meaningful
                if not response or response.strip() == "" or "not able to provide assistance" in response:
                    debug_info += "\nReceived empty or rejection response from LLM"
                    fallback_response = "I apologize, but I couldn't analyze this image properly. This could be due to image quality, format issues, or content restrictions. Please try a different medical image or rephrase your question to be more specific about what you'd like to know about the image."
                    response = fallback_response
                else:
                    debug_info += f"\nReceived valid response of {len(response)} chars"
                
                # Convert response to speech and save as output.mp3
                audio_output_path = "output.mp3"
                text_to_speech(response, audio_output_path)
                
                # Update session state
                st.session_state.response = response
                st.session_state.audio_path = audio_output_path
                st.session_state.submitted = True
                st.session_state.debug_info = debug_info
                
            except Exception as e:
                debug_info += f"\nError in LLM call: {str(e)}"
                st.error(f"Error getting response from LLM: {str(e)}")
                st.session_state.response = "I apologize, but I encountered an error while analyzing this image. Please try again with a different image or question."
                st.session_state.submitted = True
                st.session_state.debug_info = debug_info
            
            # Clean up temporary file
            try:
                os.remove(temp_image_path)
            except:
                pass
            
        except Exception as e:
            st.error(f"An error occurred during image processing: {str(e)}")
            st.session_state.response = "I encountered an error while processing your image. Please make sure you've uploaded a valid medical image and try again."
            st.session_state.submitted = True

def record_voice():
    """Record and transcribe audio"""
    try:
        with st.spinner("Recording your question..."):
            path = "input.mp3"
            # Record audio and save as input.mp3
            record_audio(file_path=path)
            
        with st.spinner("Transcribing your question..."):
            # Transcribe the audio
            transcription = transcription_groq(path)
            
            # Store the transcription in session state
            # We don't directly modify st.session_state.question which would cause an error
            st.session_state.voice_transcription = transcription
            
            # Force the app to rerun to show the transcription
            st.rerun()
            
    except Exception as e:
        st.error(f"Error recording audio: {str(e)}")

# Set up the Streamlit page with custom theme
st.set_page_config(
    page_title="Medical Image Voice Assistant",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# App header with beautiful typography
st.markdown('<h1 class="main-title">Medical Image Voice Assistant</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Your AI-powered assistant for understanding medical images. '
    'Ask questions about your medical images and receive clear, informative explanations.</p>',
    unsafe_allow_html=True
)

# Apply dark theme to the entire app (CSS moved here to ensure it loads first)
st.markdown("""
<style>
    /* Apply dark theme to the entire app */
    .stApp {
        background-color: #121212;
        color: white;
    }
    
    .main-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: #ffffff;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .subtitle {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.2rem;
        color: #cccccc;
        margin-bottom: 2rem;
        text-align: center;
        line-height: 1.6;
    }
    
    .section-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        font-size: 1.5rem;
        color: #ffffff;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #333333;
    }
    
    /* Override Streamlit's default styles */
    .stTextInput > label, .stTextArea > label, .stFileUploader > label {
        color: #ffffff !important;
    }
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    .stFileUploader > div > div {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }
    
    /* Button styles */
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-weight: 600;
        background-color: #0066CC;
        color: white;
    }
    
    .stButton button:hover {
        background-color: #0052a3;
    }
    
    /* Response and results styling */
    .response-box {
        background-color: #1e1e1e;
        border-left: 5px solid #0066CC;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
        margin-bottom: 15px;
        color: white;
    }
    
    /* Dark theme for examples section */
    .examples-container {
        background-color: #121212;
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
        margin-bottom: 30px;
    }
    
    .examples-title {
        color: white;
        font-size: 1.3rem;
        margin-bottom: 20px;
        font-weight: 500;
    }
    
    .example-image-container {
        background-color: #1e1e1e;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 15px;
    }
    
    .example-question {
        color: white;
        font-size: 1rem;
        font-style: italic;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #aaaaaa;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #333333;
    }
</style>
""", unsafe_allow_html=True)

# Main input container
with st.container():
    # Text question input (first in the flow)
    st.markdown('<div class="section-header">Ask Your Question</div>', unsafe_allow_html=True)
    
    # Initialize question from voice transcription if available
    question_value = ""
    if 'voice_transcription' in st.session_state and st.session_state.voice_transcription:
        question_value = st.session_state.voice_transcription
        # Clear the transcription after it's been used
        st.session_state.voice_transcription = None
        st.success("Voice recording transcribed!")
    elif 'question' in st.session_state:
        question_value = st.session_state.question
    
    st.text_area(
        "Enter your question about the medical image",
        value=question_value,
        key="question",
        placeholder="What can you tell me about this image?",
        height=100
    )
    
    # Voice recording option (second in the flow)
    st.markdown('<div class="section-header">Or Record Your Question</div>', unsafe_allow_html=True)
    
    record_button = st.button("📣 Record Voice Question", use_container_width=True)
    if record_button:
        record_voice()
    
    # Image upload option (third in the flow)
    st.markdown('<div class="section-header">Upload Your Medical Image</div>', unsafe_allow_html=True)
    
    # FIX: Added a proper label to the file uploader to address accessibility warning
    uploaded_file = st.file_uploader("Upload a medical image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state.processed_image = image
        st.image(image, use_container_width=True)
    
    # Submit button (fourth in the flow)
    submit_button = st.button("Submit", type="primary", use_container_width=True)
    if submit_button:
        process_query()

# Show results only after submission
if st.session_state.submitted:
    st.markdown('<div class="section-header" style="color: white; border-bottom: 2px solid #333;">Results</div>', unsafe_allow_html=True)
    
    # Display text response
    st.markdown('<div style="background-color: #121212; padding: 20px; border-radius: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: white; margin-bottom: 15px;">Assistant\'s Response:</h3>', unsafe_allow_html=True)
    st.markdown(f'<div style="background-color: #1e1e1e; color: white; padding: 15px; border-radius: 5px; border-left: 5px solid #0066CC; font-size: 16px;">{st.session_state.response}</div>', unsafe_allow_html=True)
    
    # Display audio response
    st.markdown('<h3 style="color: white; margin-top: 20px; margin-bottom: 15px;">Spoken Response:</h3>', unsafe_allow_html=True)
    if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
        st.audio(st.session_state.audio_path)
    
    # Add debug information in a collapsible section (only visible in development)
    if 'debug_info' in st.session_state:
        with st.expander("Debug Information (Developers Only)"):
            st.code(st.session_state.debug_info)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Examples at the bottom (display only, no interaction)
st.markdown("""
<div class="examples-container">
    <div class="examples-title">These examples show the types of medical images and questions you can ask:</div>
</div>
""", unsafe_allow_html=True)

# Create a 3-column layout for examples
cols = st.columns(3)

# Example 1
with cols[0]:
    if os.path.exists("example_images/xray.jpg"):
        # FIX: Added proper image caption for accessibility
        st.image("example_images/xray.jpg", caption="X-ray image example", use_container_width=True)
    else:
        st.markdown("*X-ray image*")
    st.markdown("<p class='example-question'>Example question:<br>What does this X-ray show?</p>", unsafe_allow_html=True)

# Example 2
with cols[1]:
    if os.path.exists("example_images/mri.jpg"):
        # FIX: Added proper image caption for accessibility
        st.image("example_images/mri.jpg", caption="MRI scan example", use_container_width=True)
    else:
        st.markdown("*MRI image*")
    st.markdown("<p class='example-question'>Example question:<br>Is there anything concerning in this MRI?</p>", unsafe_allow_html=True)

# Example 3
with cols[2]:
    if os.path.exists("example_images/ultrasound.jpg"):
        # FIX: Added proper image caption for accessibility
        st.image("example_images/ultrasound.jpg", caption="Ultrasound image example", use_container_width=True)
    else:
        st.markdown("*Ultrasound image*")
    st.markdown("<p class='example-question'>Example question:<br>Can you explain what I'm seeing in this ultrasound?</p>", unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">This tool is for informational purposes only and is not a substitute for professional medical advice.</div>', unsafe_allow_html=True)