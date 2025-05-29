#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load GOOGLE_API_KEY from .env (if present)
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables. Please set it in a .env file or export it.")
    exit(1)

genai.configure(api_key=api_key)
models = genai.list_models()
print("Available models:")
for m in models:
    print(f"– {m.name} (supported methods: {m.supported_generation_methods})") 