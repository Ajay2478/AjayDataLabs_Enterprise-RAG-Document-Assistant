import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
    exit()

# 2. Configure the SDK
genai.configure(api_key=api_key)

print("--- Listing Available Models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")