# config.py
# Central place for all constants used across the CAPE backend.
# Keeping them here means role thresholds and score weights can be tuned
# without touching any node logic in nodes.py.

# ── LLM ───────────────────────────────────────────────────────────────────────
# Used by get_llm() in llm.py to initialise the shared ChatGoogleGenerativeAI
# client. All three LLM nodes (batting_insight, bowling_insight,
# insight_generator) share that single client instance.

MODEL_NAME  = "gemini-3.1-flash-lite-preview"
TEMPERATURE = 0.4   # lower = more deterministic / factual; range 0.0–1.0

# ── Player Role Thresholds ────────────────────────────────────────────────────
# Used exclusively in performance_fusion_node to assign a player_role string.
# The role classifier runs three decision paths:
#
#   Pure batsman  (balls > 0, overs == 0):
#     strike_rate >= STRIKE_RATE_POWER_HITTER  →  "power_hitter"
#     strike_rate <  STRIKE_RATE_POWER_HITTER  →  "top_order_anchor"
#
#   Pure bowler   (overs > 0, balls == 0):
#     economy_rate <= ECONOMY_CONTROLLER       →  "economy_controller"
#     economy_rate >  ECONOMY_CONTROLLER       →  "death_over_specialist"
#
#   All-rounder   (both disciplines present):
#     strike_rate >= STRIKE_RATE_POWER_HITTER  →  "power_hitter"
#     strike_rate <= STRIKE_RATE_ANCHOR        →  "top_order_anchor"
#     economy_rate <= ECONOMY_CONTROLLER
#       AND wickets >= WICKETS_ALL_ROUNDER     →  "economy_controller"
#     wickets >= WICKETS_ALL_ROUNDER
#       AND strike_rate > STRIKE_RATE_ANCHOR   →  "balanced_all_rounder"
#     (fallback)                               →  "death_over_specialist"

STRIKE_RATE_POWER_HITTER = 150   # SR ≥ this → attacking / power-hitting role
STRIKE_RATE_ANCHOR       = 100   # SR ≤ this → defensive / anchor role

ECONOMY_CONTROLLER       = 7.0   # ER ≤ this → miserly / control bowler role

WICKETS_ALL_ROUNDER      = 2     # minimum wickets required for all-rounder paths

# ── Impact Score Weights ──────────────────────────────────────────────────────
# Used in performance_fusion_node when BOTH disciplines are present.
# batting_score and bowling_score are each normalised to 0–100 before weighting.
#
# When only one discipline is active the full score (0–100) comes from that
# discipline alone — these weights are NOT applied in that case.
#
# Must sum to 1.0.

BATTING_WEIGHT = 0.5
BOWLING_WEIGHT = 0.5
