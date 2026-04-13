# llm.py
# Factory function that creates and returns the LLM client.
#
# Why import from config.py?
#   MODEL_NAME and TEMPERATURE are defined once in config.py.
#   If you ever want to switch models or tune temperature, change it there —
#   not scattered across multiple files.
#
# Why a factory function and not a module-level instance?
#   load_dotenv() must run before the LLM client is created (it needs the API key).
#   load_dotenv() is called in app.py at startup.
#   get_llm() is called in nodes.py at module level — after app.py has already
#   loaded the env vars — so the key is available in time.

from langchain_google_genai import ChatGoogleGenerativeAI
from config import MODEL_NAME, TEMPERATURE


def get_llm():
    """Return a configured Gemini chat model instance."""
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=TEMPERATURE
    )
