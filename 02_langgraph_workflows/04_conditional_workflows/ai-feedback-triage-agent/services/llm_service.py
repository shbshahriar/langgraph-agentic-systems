from langchain_anthropic import ChatAnthropic

from config.settings import MODEL_NAME, TEMPERATURE, TIMEOUT_SECONDS


def get_llm() -> ChatAnthropic:
    return ChatAnthropic(
        model_name=MODEL_NAME,
        temperature=TEMPERATURE,
        timeout=TIMEOUT_SECONDS,
        stop=None,
    )
