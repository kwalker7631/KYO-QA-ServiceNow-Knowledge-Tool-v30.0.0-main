"""Utility helpers for summarizing run results."""

def build_summary_message(pass_count: int, fail_count: int, review_count: int) -> str:
    """Return a formatted summary message for job completion."""
    return (
        f"Pass: {pass_count}\n"
        f"Fail: {fail_count}\n"
        f"Review: {review_count}"
    )
