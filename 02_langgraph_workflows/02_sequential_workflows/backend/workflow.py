from langgraph.graph import StateGraph,START, END
from state import NoteState
from nodes import generate_outline, generate_notes, generate_summary

graph= StateGraph(NoteState)

graph.add_node("outline", generate_outline)
graph.add_node("notes", generate_notes)
graph.add_node("summary", generate_summary)

graph.add_edge(START, "outline")
graph.add_edge("outline", "notes")
graph.add_edge("notes", "summary")
graph.add_edge("summary", END)

workflow = graph.compile()