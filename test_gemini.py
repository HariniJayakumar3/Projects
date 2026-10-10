
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Gemini API key not found. Check your .env file.")
else:
    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Reply with exactly: GCC Compass AI is working!"
        )

        print(response.text)

    except Exception as e:
        print("Gemini API request failed:", e)
