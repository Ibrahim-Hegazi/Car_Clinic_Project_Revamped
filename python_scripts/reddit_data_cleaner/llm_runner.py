# Responsible for model communication and logic tied to prompt creation and LLM parsing.

import json
from ollama import Client
from postprocessor import format_top_comments_json_style

client = Client(host='http://localhost:11434')



# System prompt used across all requests
SYSTEM_PROMPT = """### SYSTEM TASK ###
            You are an automotive expert assistant helping extract structured knowledge from car repair discussions for a mechanic-assist chatbot and emergency troubleshooting system.

            Your job is to extract a clear "problem" and the best matching "solution" from real Reddit car-related posts.

            Your output will be used to train and fine-tune a support chatbot for a company called Car Clinic.

            ---

            ### INSTRUCTIONS ###
            1. Carefully read the post title, self-text, and top comment (The top comments include 1 to 3 comments,where each comment start from starts with the comments user then the score; for example, FriendlySociety3831 (Score: 3): ).
            2. Determine if the post includes a **specific, actionable car problem**.
            3. Determine if the comment provides a **mechanically sound, complete solution**.
            4. If either of these is missing, return:  
            ```json
            {"is_valid": false, "problem": null, "solution": null}
            ```
            5. If both are present, return in the format below:
            ```json
            {"is_valid": true, "problem": "...", "solution": "..."}
            ```
            6. If is_valid is true, then add suggested general extra help in another row:
            ```json
            {"is_valid": true, "problem": "...", "solution": "...", "Extra General Help": "..."}
            ```
            7. Output only one single valid JSON object following the rules above.
            Do NOT include any explanation or extra text. Output only JSON.

            """


def build_prompt(title, selftext, comments):
    return f"""{SYSTEM_PROMPT}
        POST TITLE
        {title}

        POST BODY
        {selftext}

        TOP COMMENTS
        {comments}

        YOUR RESPONSE (JSON ONLY, NO EXPLANATION)
        """


def call_llm_and_parse(prompt: str, idx: int, logger):
    try:
        response = client.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        response_text = response['message']['content'].strip()
        logger.info(f"🔁 Raw model response for row {idx}:\n{response_text}")
        parsed = json.loads(response_text)
        if parsed.get("is_valid"):
            parsed.setdefault("Extra General Help", "")
            return parsed, None
        return None, None
    except json.JSONDecodeError as e:
        logger.error(f"⚠️ JSON parsing failed at row {idx}: {e}")
        return None, {"row": idx, "error": "JSONDecodeError", "text": response_text}
    except Exception as e:
        logger.error(f"❌ Unexpected error at row {idx}: {e}")
        return None, {"row": idx, "error": str(e), "prompt": prompt}


# def clean_single_row(row, idx, logger):
#     title = row.get("title", "")
#     selftext = row.get("selftext", "")
#     raw_comments = row.get("top_comments", "")
#     if not title.strip() and not selftext.strip():
#         return None, None
#     formatted_comments = format_top_comments_json_style(raw_comments)
#     prompt = build_prompt(title, selftext, formatted_comments)
#     logger.info(f"\n\n🔍 [Row {idx}] Prompt:\n{'=' * 40}\n{prompt}\n{'=' * 40}\n")
#     return call_llm_and_parse(prompt, idx, logger)
def clean_single_row(row, idx, logger):
    post_id = row.get("id", "")
    title = row.get("title", "")
    selftext = row.get("selftext", "")
    raw_comments = row.get("top_comments", "")

    if not title.strip() and not selftext.strip():
        return None, None

    formatted_comments = format_top_comments_json_style(raw_comments)
    prompt = build_prompt(title, selftext, formatted_comments)
    logger.info(f"\n\n🔍 [Row {idx}] Prompt:\n{'=' * 40}\n{prompt}\n{'=' * 40}\n")

    result, error = call_llm_and_parse(prompt, idx, logger)

    if result:
        result["post_id"] = post_id  

    return result, error


# DONEEEEEEEEE