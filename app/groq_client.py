import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

def groq_summarize(transcript: str, prompt: str = "") -> str:
    full_prompt = (prompt + "\n\n") if prompt else ""
    full_prompt += transcript
    resp = groq.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": full_prompt}]
    )
    return resp.choices[0].message.content