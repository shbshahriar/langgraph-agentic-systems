from langgraph.graph import StateGraph, START, END
from app.state import TweetState
from app.nodes.generate import generate_tweet
from app.nodes.evaluate import evaluate_tweet
from app.nodes.optimize import optimize_tweet
from app.routers.evaluation_router import route_evaluation

graph = StateGraph(TweetState)

graph.add_node('generate', generate_tweet)
graph.add_node('evaluate', evaluate_tweet)
graph.add_node('optimize', optimize_tweet)

graph.add_edge(START, 'generate')
graph.add_edge('generate', 'evaluate')
graph.add_conditional_edges('evaluate', route_evaluation, {'approved': END, 'needs_improvement': 'optimize'})
graph.add_edge('optimize', 'evaluate')

workflow = graph.compile()
