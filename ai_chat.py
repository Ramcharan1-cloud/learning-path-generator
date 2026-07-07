import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def tutor_reply(user_message, learning_goal, roadmap):

    prompt = f"""
You are an expert AI tutor.

Student Goal:
{learning_goal}

Roadmap:
{roadmap}

Student Question:
{user_message}

Explain step-by-step with simple examples.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Error: {e}"