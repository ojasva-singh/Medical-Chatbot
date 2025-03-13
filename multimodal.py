import os
from dotenv import load_dotenv
import base64
from groq import Groq

#Load env variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Write the path of the image you want to be analyzed
img_path = "acne.jpg"

img_file = open(img_path, "rb")
enc_img = base64.b64encode(img_file.read()).decode("utf-8")

# Multimodal query
client = Groq()
model = "llama-3.2-90b-vision-preview"
query = "What is the medical condition in the image?"

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": query
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{enc_img}"
                }
            }
        ]
    }
]

chat = client.chat.completions.create(messages=messages, model=model)

print(chat.choices[0].message.content)  
