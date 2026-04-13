# reducers.py
# Reducer functions for merging parallel node outputs into shared state.
#
# ── What is a reducer? ────────────────────────────────────────────────────────
# When two nodes run in parallel and both write to the same state key,
# LangGraph calls the reducer to decide the final value.
#
# The reducer receives:
#   old  — the current value already in state
#   new  — the value the node just returned
#
# It returns the merged result that goes back into state.
#
# Think of it like: final_value = reducer(old_value, new_value)
# ─────────────────────────────────────────────────────────────────────────────


def merge_batting_metrics(old: dict | None, new: dict) -> dict:
    """Merge a new batting metric into the existing batting_metrics dict.

    Each batting node returns one key-value pair, e.g. {"strike_rate": 145.2}.
    This reducer accumulates all of them into a single dict.

    Example:
        old = {"strike_rate": 145.2}
        new = {"boundary_ratio": 0.6}
        result → {"strike_rate": 145.2, "boundary_ratio": 0.6}
    """
    return {**(old or {}), **new}


def merge_bowling_metrics(old: dict | None, new: dict) -> dict:
    """Merge a new bowling metric into the existing bowling_metrics dict.

    Same pattern as merge_batting_metrics but for bowling nodes.

    Example:
        old = {"economy_rate": 6.5}
        new = {"bowling_average": 22.0}
        result → {"economy_rate": 6.5, "bowling_average": 22.0}
    """
    return {**(old or {}), **new}

def merge_performance_metrics(old: dict | None, new: dict) -> dict:
    """Merge batting and bowling metrics into a single performance_metrics dict.

    This reducer combines the outputs of the parallel batting and bowling
    workflows into one comprehensive performance_metrics dict.

    Example:
        old = {"strike_rate": 145.2, "boundary_ratio": 0.6}
        new = {"economy_rate": 6.5, "bowling_average": 22.0}
        result → {
            "strike_rate": 145.2,
            "boundary_ratio": 0.6,
            "economy_rate": 6.5,
            "bowling_average": 22.0
        }
    """
    return {**(old or {}), **new}
