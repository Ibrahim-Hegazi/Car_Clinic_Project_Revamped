import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from llama_cpp import Llama

# === Step 1: Paths === #
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DATA_DIR = PROJECT_ROOT / "data" / "cleaned"
MODEL_PATH = PROJECT_ROOT / "models" / "TheDataCleaningModel" / "deepseek-coder-6.7b-instruct.Q5_K_M.gguf"

# === Step 2: Load GGUF Model === #
print("🚀 Loading local GGUF model...")
llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=4096,
    n_threads=8,      # Adjust based on your CPU
    n_batch=8,
    verbose=False
)

# === Step 3: Prompt Template === #
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
        If both are present, return in the format below:
        {"is_valid": true, "problem": "...", "solution": "..."}
        5. If is_valid is true, then add suggested general extra help in another row:
        {"is_valid": true, "problem": "...", "solution": "..." , "Extra General Help": "..."}
        """



# === Step 4: Scan for New Files ===
# === Step 4: Find Raw Files to Clean === #
print("🔎 Scanning for raw files that haven't been cleaned...")

queued_files = []
raw_files = list(RAW_DATA_DIR.glob("Reddit_CarAdvice_*.csv"))

for raw_file in raw_files:
    date_str = raw_file.stem.replace("Reddit_CarAdvice_", "")
    cleaned_file = CLEANED_DATA_DIR / f"Reddit_CarAdvice_Cleaned_{date_str}.csv"
    if not cleaned_file.exists():
        queued_files.append((raw_file, cleaned_file))
    else:
        print(f"⏭️ Skipping {raw_file.name} → Already cleaned.")

if not queued_files:
    print("🎉 All unprocessed files cleaned and saved successfully.")
    exit(0)

print(f"📝 Files to process: {[f[0].name for f in queued_files]}")
print(f"📁 Target cleaned outputs: {[f[1].name for f in queued_files]}")



# === Step 5: Process Each Raw File ===
for raw_file, cleaned_file in queued_files:
    print(f"\n🔧 Processing: {raw_file.name}")
    df = pd.read_csv(raw_file)

    results = []
    skipped_count = 0

    for idx, row in df.iterrows():
        title = row.get("title", "")
        selftext = row.get("selftext", "")
        comment = row.get("top_comment", "")

        # Skip empty posts
        if not title.strip() and not selftext.strip():
            skipped_count += 1
            continue

        prompt = f"""{SYSTEM_PROMPT}

                ### POST TITLE ###
                {title}
                
                ### POST BODY ###
                {selftext}
                
                ### TOP COMMENTS ###
                {comment}
                
                ### JSON OUTPUT ###
                """

        # ===== ADD THIS LINE TO PRINT THE PROMPT =====
        print("=== PROMPT SENT TO LLM ===\n", prompt, "\n" + "=" * 50 + "\n")

        response = llm(prompt, stop=["</s>"], max_tokens=512)
        response_text = response["choices"][0]["text"].strip()

        try:
            parsed = json.loads(response_text)
            if parsed.get("is_valid"):
                results.append(parsed)
        except Exception as e:
            print(f"⚠️ Error parsing response at row {idx}: {e}")
            skipped_count += 1

    # Convert to DataFrame and Save
    cleaned_df = pd.DataFrame(results)
    cleaned_df.to_csv(cleaned_file, index=False)
    print(f"✅ Cleaned data saved: {cleaned_file}")
    print(f"📊 Stats for {raw_file.name}:")
    print(f"    Total rows: {len(df)}")
    print(f"    Cleaned entries: {len(results)}")
    print(f"    Skipped: {skipped_count}")


# for date_str, raw_file, cleaned_file in queued_files:
#     print(f"⚙️ Processing: {raw_file}")
#     # Create cleaned output directory if needed
#     cleaned_file.parent.mkdir(parents=True, exist_ok=True)
#
#     # Load raw data
#     df = pd.read_csv(raw_file).head(10)
#     results = []
#
#     for _, row in df.iterrows():
#         title = str(row.get("title", ""))
#         body = str(row.get("selftext", ""))
#         comment = str(row.get("top_comment", ""))
#
#         # Skip empty data
#         if not (title or body or comment):
#             continue
#
#         prompt = f"""{SYSTEM_PROMPT}
#             REDDIT POST
#             TITLE: {title}
#             BODY: {body}
#             TOP_COMMENT: {comment}
#
#             RESPONSE
#             """
#         try:
#             response = llm(prompt=prompt, max_tokens=512, stop=["###"])
#             raw_output = response["choices"][0]["text"].strip()
#
#             # Try parsing the output
#             parsed = json.loads(raw_output)
#             parsed["raw_output"] = raw_output
#         except Exception as e:
#             parsed = {
#                 "is_valid": False,
#                 "problem": None,
#                 "solution": None,
#                 "raw_output": f"ERROR: {str(e)}"
#             }
#
#         results.append(parsed)
#
#     # Convert to DataFrame and Save
#     cleaned_df = pd.DataFrame(results)
#     cleaned_df.to_csv(cleaned_file, index=False)
#     print(f"✅ Cleaned data saved: {cleaned_file}")

print("🎉 All unprocessed files cleaned and saved successfully.")