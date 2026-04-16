from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "claude-haiku-4-5"
TEMPERATURE = 0.2
TIMEOUT_SECONDS = 60

CRITICAL_PRIORITY = "P0"
URGENCY_TO_PRIORITY = {
    "critical": "P0",
    "high": "P1",
    "medium": "P2",
    "low": "P3",
}
