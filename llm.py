import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class LLM:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_text(
        self,
        prompt,
        model="gemma-4-31b-it",
        max_tokens=2000,
        temperature=0.3
    ):
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
            )
        )
        return response.text