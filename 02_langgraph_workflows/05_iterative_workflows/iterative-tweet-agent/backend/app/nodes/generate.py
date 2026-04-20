from langchain_core.messages import SystemMessage, HumanMessage
from app.llm.models import generator_llm
from app.state import TweetState


def generate_tweet(state: TweetState):

    messages = [
        SystemMessage(content="You are a deliberately bad Twitter/X writer whose job is to produce the worst possible first draft."),
        HumanMessage(content=f"""
Write the worst possible tweet on the topic: "{state['topic']}".

Rules:
- Max 280 characters.
- Make it boring, generic, awkward, and unfunny.
- It should feel low-effort and easy to criticize.
- Prefer flat statements, clichés, or weak phrasing.
- Do not try to be clever, viral, or polished.
""")
    ]

    raw = generator_llm.invoke(messages).content
    response = raw if isinstance(raw, str) else ''.join(
        block['text'] for block in raw if isinstance(block, dict) and block.get('type') == 'text'
    )

    return {'tweet': response, 'tweet_history': [response]}
