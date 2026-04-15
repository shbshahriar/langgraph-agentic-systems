# =============================================================================
# llm.py — LLM factory for the Parallel Writing Assessment Engine
#
# This file has ONE job: create and return a configured Claude LLM instance.
#
# WHY A FACTORY FUNCTION instead of a module-level instance?
#   If we did this at module level:
#       llm = ChatAnthropic(model=MODEL_NAME)   ← runs immediately on import
#
#   The problem: ANTHROPIC_API_KEY must be loaded from .env BEFORE this line runs.
#   load_dotenv() is called in app.py at startup — but nodes.py imports llm.py
#   at module level too, which means the LLM would be created before the key loads.
#
#   Solution: wrap it in get_llm() — a function that is only CALLED later (inside
#   nodes), by which time app.py has already run load_dotenv() and the key exists.
#
# WHY langchain-anthropic?
#   It wraps the Claude API with LangChain's standard interface.
#   Every node calls llm.invoke(prompt) — same pattern regardless of which
#   LLM provider is underneath. Swapping models = change config.py only.
#
# WHY claude-haiku-4-5?
#   We have 9 nodes running in parallel, each making an LLM call.
#   Haiku is the fastest and most cost-efficient Claude model —
#   perfect for structured scoring tasks that don't need deep reasoning.
#   For a more thorough analysis, swap MODEL_NAME in config.py to claude-sonnet-4-6.
#
# DEPENDENCY:
#   pip install langchain-anthropic
#   ANTHROPIC_API_KEY must be set in your .env file
# =============================================================================

from langchain_anthropic import ChatAnthropic
from config import MODEL_NAME, TEMPERATURE


def get_llm() -> ChatAnthropic:
    """
    Create and return a configured Claude chat model instance.

    Called inside nodes.py at module level — by the time nodes.py is imported,
    app.py has already called load_dotenv() so ANTHROPIC_API_KEY is available.

    Returns:
        ChatAnthropic: a LangChain-wrapped Claude model ready to call .invoke()
    """
    return ChatAnthropic(
        model_name=MODEL_NAME,
        temperature=TEMPERATURE,
        timeout=120,
        stop=None
    )
