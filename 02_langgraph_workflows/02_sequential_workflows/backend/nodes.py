from prompts import outline_prompt, notes_prompt, summary_prompt
from state import NoteState
from llm import get_llm

llm = get_llm()

def generate_outline(state: NoteState) -> dict:
    response = llm.invoke(outline_prompt(state['topic']))
    return {'outline': response.content}

def generate_notes(state: NoteState) -> dict:
    response = llm.invoke(notes_prompt(state['topic'], state.get('outline', '')))
    return {'notes': response.content}

def generate_summary(state: NoteState) -> dict:
    response = llm.invoke(summary_prompt(state['topic'], state.get('notes', '')))
    return {'summary': response.content}
