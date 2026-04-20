from langchain_core.messages import SystemMessage, HumanMessage
from app.llm.models import optimizer_llm
from app.state import TweetState


def optimize_tweet(state: TweetState):

    messages = [
        SystemMessage(content="You punch up tweets for virality and humor based on given feedback."),
        HumanMessage(content=f"""
Improve the tweet based on this feedback:
"{state['feedback']}"

Topic: "{state['topic']}"
Original Tweet:
{state['tweet']}

Re-write it as a short, viral-worthy tweet. Avoid Q&A style and stay under 280 characters.
""")
    ]

    raw = optimizer_llm.invoke(messages).content
    response = raw if isinstance(raw, str) else ''.join(
        block['text'] for block in raw if isinstance(block, dict) and block.get('type') == 'text'
    )
    iteration = state['iteration'] + 1

    return {'tweet': response, 'iteration': iteration, 'tweet_history': [response]}
