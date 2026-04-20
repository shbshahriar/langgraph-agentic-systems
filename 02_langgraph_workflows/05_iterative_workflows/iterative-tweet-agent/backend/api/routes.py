from fastapi import APIRouter
from schemas.request_schema import TweetRequest
from app.graph import workflow

router = APIRouter()


@router.post("/generate")
def generate(request: TweetRequest):

    initial_state = {
        "topic": request.topic,
        "iteration": 1,
        "max_iteration": request.max_iteration,
        "tweet_history": [],
        "feedback_history": [],
    }

    result = workflow.invoke(initial_state)

    return {
        "tweet": result["tweet"],
        "evaluation": result["evaluation"],
        "feedback": result["feedback"],
        "iteration": result["iteration"],
        "tweet_history": result["tweet_history"],
        "feedback_history": result["feedback_history"],
    }
