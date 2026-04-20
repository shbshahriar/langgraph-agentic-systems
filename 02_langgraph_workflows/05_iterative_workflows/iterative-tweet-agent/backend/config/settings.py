import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
