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
        1. Carefully read the post title, self-text, and top comment.
        2. Determine if the post includes a **specific, actionable car problem**.
        3. Determine if the comment provides a **mechanically sound, complete solution**.
        4. If either of these is missing, return:  
        ```json
        {"is_valid": false, "problem": null, "solution": null}
        If both are present, return in the format below:
        {"is_valid": true, "problem": "...", "solution": "..."}
        """

# === Step 4: Scan for New Files ===
print("🔎 Scanning for raw files that haven't been cleaned...")
raw_dirs = [p for p in RAW_DATA_DIR.iterdir() if p.is_dir()]
queued_files = []

for raw_dir in raw_dirs:
    date_str = raw_dir.name
    raw_file = raw_dir / "raw_reddit_data.csv"
    cleaned_file = CLEANED_DATA_DIR / date_str / "cleaned_reddit_data.csv"
    if not cleaned_file.exists() and raw_file.exists():
        queued_files.append((date_str, raw_file, cleaned_file))
    if not queued_files:
        print("✅ All available raw data already cleaned. No work needed.")
        exit()



# === Step 5: Process Each Raw File ===
for date_str, raw_file, cleaned_file in queued_files:
    print(f"⚙️ Processing: {raw_file}")
    # Create cleaned output directory if needed
    cleaned_file.parent.mkdir(parents=True, exist_ok=True)

    # Load raw data
    df = pd.read_csv(raw_file)
    results = []

    for _, row in df.iterrows():
        title = str(row.get("title", ""))
        body = str(row.get("selftext", ""))
        comment = str(row.get("top_comment", ""))

        # Skip empty data
        if not (title or body or comment):
            continue

        prompt = f"""{SYSTEM_PROMPT}
            REDDIT POST
            TITLE: {title}
            BODY: {body}
            TOP_COMMENT: {comment}
    
            RESPONSE
            """
        try:
            response = llm(prompt=prompt, max_tokens=512, stop=["###"])
            raw_output = response["choices"][0]["text"].strip()

            # Try parsing the output
            parsed = json.loads(raw_output)
            parsed["raw_output"] = raw_output
        except Exception as e:
            parsed = {
                "is_valid": False,
                "problem": None,
                "solution": None,
                "raw_output": f"ERROR: {str(e)}"
            }

        results.append(parsed)

    # Convert to DataFrame and Save
    cleaned_df = pd.DataFrame(results)
    cleaned_df.to_csv(cleaned_file, index=False)
    print(f"✅ Cleaned data saved: {cleaned_file}")

print("🎉 All unprocessed files cleaned and saved successfully.")