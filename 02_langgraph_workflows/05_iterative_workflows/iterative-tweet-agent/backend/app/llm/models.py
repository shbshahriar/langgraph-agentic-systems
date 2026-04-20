from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from config.settings import GEMINI_MODEL, ANTHROPIC_MODEL
from schemas.evaluation_schema import TweetEvaluation

generator_llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)
optimizer_llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)

evaluator_llm = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)
structured_evaluator_llm = evaluator_llm.with_structured_output(TweetEvaluation)
