def outline_prompt(topic: str) -> str:
    return f"Create an outline for a note on the topic in just 5 points: {topic}"

def notes_prompt(topic: str, outline: str) -> str:
    return f"Based on the following outline, write detailed notes on the topic but not more than 500 char: {topic}\n\nOutline:\n{outline}"

def summary_prompt(topic: str, notes: str) -> str:
    return f"Summarize the following notes on the topic but not more than 50 characters: {topic}\n\nNotes:\n{notes}"