# reddit_data_cleaner/cleaner.py

import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path
from ollama import Client
import logging

client = Client(host='http://localhost:11434')  # Persistent Ollama server

def format_top_comments_json_style(raw_comment_block: str) -> str:
    comments = raw_comment_block.strip().split("\n")
    formatted = []
    count = 1

    for comment in comments:
        if not comment.strip():
            continue

        # Extract just the actual comment text (after the first colon)
        try:
            comment_text = comment.split(":", 1)[2].strip()
        except IndexError:
            comment_text = comment.strip()

        formatted.append({f"Comment {count}": comment_text})
        count += 1

    # Turn into pretty JSON-style string
    import json
    return "TOP COMMENTS\n" + json.dumps(formatted, indent=2)


def run_llm_cleaning_logic(logger=None):

    if logger is None:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("LLM Cleaner")

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
    CLEANED_DATA_DIR = PROJECT_ROOT / "data" / "cleaned"

    if not RAW_DATA_DIR.exists():
        logger.error(f"❌ RAW data directory not found: {RAW_DATA_DIR}")
        return
    if not CLEANED_DATA_DIR.exists():
        logger.warning(f"📂 Creating missing cleaned data directory: {CLEANED_DATA_DIR}")
        CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)

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
            """



    today_str = datetime.now().strftime("%Y-%m-%d")
    raw_file = RAW_DATA_DIR / f"Reddit_CarAdvice_{today_str}.csv"
    cleaned_file = CLEANED_DATA_DIR / f"Reddit_CarAdvice_Cleaned_{today_str}.csv"

    logger.info(f"🔍 Looking for today’s file: {raw_file.name}")

    if not raw_file.exists():
        logger.warning("⏭️ Today's raw file not found. Skipping cleaning.")
        return

    if cleaned_file.exists():
        logger.info("✅ Already cleaned today’s file.")
        return

    logger.info(f"📥 Reading raw CSV: {raw_file}")
    df = pd.read_csv(raw_file)
    logger.info(f"✅ Loaded {len(df)} rows from raw data.")
    results = []
    skipped_count = 0
    failure_log = []

    start_time = time.time()

    for idx, row in df.iterrows():
        title = row.get("title", "")
        selftext = row.get("selftext", "")
        # comment = row.get("top_comments", "")
        raw_comment_block = row.get("top_comments", "")
        comment = format_top_comments_json_style(raw_comment_block)


        if not title.strip() and not selftext.strip():
            skipped_count += 1
            continue

        prompt = f"""{SYSTEM_PROMPT}
                POST TITLE
                {title}
                
                POST BODY
                {selftext}
                
                TOP COMMENTS
                {comment}
                
                JSON OUTPUT
                """
        logger.info(f"\n\n🔍 [Row {idx}] Prompt:\n{'=' * 40}\n{prompt}\n{'=' * 40}\n")
        # logger.debug(f"🔁 Cleaning row {idx} - prompt:\n{prompt}")  # Showing the prompt before sending it to the cleaning model
        # logger.debug(f"🔁 Cleaning row {idx} - sending prompt to Ollama.")

        try:
            response = client.chat(
                model="mistral",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response['message']['content'].strip()
            parsed = json.loads(response_text)

            if parsed.get("is_valid"):
                # Ensure schema consistency
                if "Extra General Help" not in parsed:
                    parsed["Extra General Help"] = ""
                results.append(parsed)
        except json.JSONDecodeError as e:
            logger.error(f"⚠️ JSON parsing failed at row {idx}: {e}")
            failure_log.append({"row": idx, "error": "JSONDecodeError", "text": response_text})
            skipped_count += 1
        except Exception as e:
            logger.error(f"❌ Unexpected error at row {idx}: {e}")
            failure_log.append({"row": idx, "error": str(e), "prompt": prompt})
            skipped_count += 1


    cleaned_df = pd.DataFrame(results)
    try:
        cleaned_df.to_csv(cleaned_file, index=False)
        logger.info(f"✅ Cleaned data saved successfully: {cleaned_file}")
    except Exception as e:
        logger.error(f"❌ Failed to save cleaned data: {e}")
        return

    logger.info("📊 Stats:")
    logger.info(f" Total rows: {len(df)}")
    logger.info(f" Cleaned entries: {len(results)}")
    logger.info(f" Skipped/Errors: {skipped_count}")

    if failure_log:
        error_path = cleaned_file.with_suffix(".error_log.json")
        with open(error_path, "w") as f:
            json.dump(failure_log, f, indent=2)
        logger.warning(f"🛠️ Error log saved to: {error_path}")

    elapsed = time.time() - start_time
    logger.info(f"🕒 Total cleaning time: {elapsed:.2f} seconds")

    logger.info("🎉 Cleaning completed.")
