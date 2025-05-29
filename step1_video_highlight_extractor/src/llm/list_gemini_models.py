import os
import google.generativeai as genai
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set in environment.")

    print(f"\nConfiguring Gemini with API key: {api_key[:10]}...")
    genai.configure(api_key=api_key)

    print("\nAvailable Gemini models:")
    print("-" * 50)
    try:
        for m in genai.list_models():
            print(f"\nModel: {m.name}")
            print(f"Display Name: {m.display_name}")
            print(f"Description: {m.description}")
            print(f"Generation Methods: {m.supported_generation_methods}")
            print(f"Input Types: {getattr(m, 'input_types', 'N/A')}")
            print("-" * 30)
    except Exception as e:
        print(f"Error listing models: {str(e)}")
        raise

if __name__ == "__main__":
    main() 