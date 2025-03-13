import os
from dotenv import load_dotenv
import base64
from groq import Groq

#Load env variables
load_dotenv()
GROQ_API = os.getenv("GROQ_API")

# Write the path of the image you want to be analyzed
img_path = "acne.png"

img_file = open(img_path, "rb")
enc_img = base64.b64encode(img_file.read()).decode("utf-8")

# Multimodal query
client = Groq(GROQ_API)
model = "llama-3.2-90b-vision-preview"
query = ""
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": query
            },
            {
                "type": "image",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{enc_img}"
                    },
            },
        ],
    }
]

chat = client.chat.completions.create(messages=messages, model=model)

print(chat)