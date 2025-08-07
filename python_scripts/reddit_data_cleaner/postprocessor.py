# Handles formatting, cleaning, and ensuring schema compliance for LLM responses.
    # If you're planning to add:
            # Hallucination filters
            # JSON validation/repair
            # Schema normalization
    # This is the right place.

import json

def format_top_comments_json_style(raw_comment_block: str) -> str:
    comments = raw_comment_block.strip().split("\n")
    formatted = []
    count = 1
    for comment in comments:
        if not comment.strip():
            continue
        try:
            comment_text = comment.split(":", 1)[2].strip()
        except IndexError:
            comment_text = comment.strip()
        formatted.append({f"Comment {count}": comment_text})
        count += 1
    return "\n" + json.dumps(formatted, indent=2)
