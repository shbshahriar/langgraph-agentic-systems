# config.py
# Central place for all constants used across the project.
# Instead of writing numbers directly inside nodes.py or workflow.py,
# we define them here so they are easy to find and change in one place.

# ── LLM ───────────────────────────────────────────────────────────────────────

MODEL_NAME  = "gemini-3.1-flash-lite-preview"
TEMPERATURE = 0.4   # Lower = more factual output, good for analysis tasks

# ── Player Role Thresholds ────────────────────────────────────────────────────
# These numbers decide what role label a player gets after the fusion node.
# Based on strike rate and economy rate ranges commonly used in cricket analytics.

STRIKE_RATE_POWER_HITTER   = 150   # strike rate above this → power hitter
STRIKE_RATE_ANCHOR         = 100   # strike rate below this → anchor / defensive

ECONOMY_CONTROLLER         = 7.0   # economy rate below this → economy controller
ECONOMY_EXPENSIVE          = 10.0  # economy rate above this → expensive bowler

WICKETS_ALL_ROUNDER        = 2     # minimum wickets to be considered a bowler

# ── Impact Score Weights ──────────────────────────────────────────────────────
# The fusion node combines batting and bowling into one impact score.
# These weights control how much each side contributes.
# Both must add up to 1.0

BATTING_WEIGHT  = 0.5
BOWLING_WEIGHT  = 0.5
