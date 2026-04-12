# ── llm.py ────────────────────────────────────────────────────────────────────
# Responsible for creating and returning the LLM (Large Language Model) client.
#
# Why a factory function (get_llm)?
#   Wrapping the client in a function keeps configuration in one place.
#   If you ever switch models or providers, you only change it here.
#
# Why is load_dotenv() NOT here?
#   Environment variables should be loaded once at application startup, not
#   scattered across modules. load_dotenv() is called in app.py before any
#   other imports that depend on env vars. This keeps llm.py a pure factory.
#
# Why call get_llm() once at module level in nodes.py (not here)?
#   Creating a new client on every node call is wasteful. The factory is
#   defined here and called once in nodes.py so a single instance is reused.
# ──────────────────────────────────────────────────────────────────────────────

from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm():
    """Return a configured Gemini chat model instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7   # 0 = deterministic, 1 = more creative
    )
