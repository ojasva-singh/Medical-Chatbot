import os
from dotenv import load_dotenv
import base64

#Load env variables
load_dotenv()
GROQ_API = os.getenv("GROQ_API")

# Write the path of the image you want to be analyzed
img_path = ""

img_file = open(img_path, "rb")
enc_img = base64.b64encode(img_file.read()).decode("utf-8")