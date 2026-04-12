# ── llm.py ────────────────────────────────────────────────────────────────────
# Responsible for creating and returning the LLM (Large Language Model) client.
#
# Why a factory function (get_llm)?
#   Wrapping the client in a function keeps configuration in one place.
#   If you ever switch models or providers, you only change it here.
#
# Why load_dotenv()?
#   Reads the GOOGLE_API_KEY from the .env file so it's available as an
#   environment variable before the LangChain client initialises.
#   Without this, the client would fail to authenticate.
#
# Why call get_llm() once at module level in nodes.py (not here)?
#   Creating a new client on every node call is wasteful. The factory is
#   defined here and called once in nodes.py so a single instance is reused.
# ──────────────────────────────────────────────────────────────────────────────

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env (e.g. GOOGLE_API_KEY)
load_dotenv()

def get_llm():
    """Return a configured Gemini chat model instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7   # 0 = deterministic, 1 = more creative
    )
