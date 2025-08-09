# Handles formatting, cleaning, and ensuring schema compliance for LLM responses.
    # If you're planning to add:
            # Hallucination filters
            # JSON validation/repair
            # Schema normalization
    # This is the right place.

import re
import json

def parse_multiline_comments(raw_comment_block: str) -> str:
    # Regex to detect start of a comment line: username (Score: number):
    comment_start_pattern = re.compile(r'^\S+ \(Score: \d+\):')

    comments = []
    current_comment_lines = []

    for line in raw_comment_block.splitlines():
        if comment_start_pattern.match(line):
            # If we have collected lines for a previous comment, save it
            if current_comment_lines:
                comments.append('\n'.join(current_comment_lines).strip())
            # Start new comment
            current_comment_lines = [line]
        else:
            # Continuation of current comment
            if line.strip() != '' or current_comment_lines:
                current_comment_lines.append(line)
    # Append last comment
    if current_comment_lines:
        comments.append('\n'.join(current_comment_lines).strip())

    # Format into JSON list with numbered keys
    formatted = [{f"Comment {i+1}": comment} for i, comment in enumerate(comments)]
    return "\n" + json.dumps(formatted, indent=2)

