from app.state import TweetState


def route_evaluation(state: TweetState) -> str:

    if state['evaluation'] == 'approved' or state['iteration'] >= state['max_iteration']:
        return 'approved'

    return 'needs_improvement'
