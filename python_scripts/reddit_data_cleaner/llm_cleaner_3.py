import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import subprocess

# === Step 1: Paths === #
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DATA_DIR = PROJECT_ROOT / "data" / "cleaned"

# === Step 2: Prompt Template === #
SYSTEM_PROMPT = """### SYSTEM TASK ###
You are an automotive expert assistant helping extract structured knowledge from car repair discussions for a mechanic-assist chatbot and emergency troubleshooting system.

Your job is to extract a clear \"problem\" and the best matching \"solution\" from real Reddit car-related posts.

Your output will be used to train and fine-tune a support chatbot for a company called Car Clinic.

---

### INSTRUCTIONS ###
1. Carefully read the post title, self-text, and top comment (The top comments include 1 to 3 comments, where each comment starts with the comment's user then the score; for example, FriendlySociety3831 (Score: 3): ).
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
6. If is_valid is true, then add suggested general extra help in another field:
```json
{"is_valid": true, "problem": "...", "solution": "..." , "Extra General Help": "..."}
```
"""

# === Step 3: Scan for New Files === #
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

# === Step 4: Process Each Raw File === #
for raw_file, cleaned_file in queued_files:
    print(f"\n🔧 Processing: {raw_file.name}")
    df = pd.read_csv(raw_file)

    results = []
    skipped_count = 0
    failure_log = []

    for idx, row in df.iterrows():
        title = row.get("title", "")
        selftext = row.get("selftext", "")
        comment = row.get("top_comment", "")

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

        print("=== PROMPT SENT TO OLLAMA ===\n", prompt, "\n" + "=" * 50 + "\n")

        try:
            response = subprocess.run(
                ["ollama", "run", "mistral"],
                input=prompt.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )
            response_text = response.stdout.decode("utf-8").strip()
            parsed = json.loads(response_text)

            if parsed.get("is_valid"):
                results.append(parsed)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed at row {idx}: {e}")
            failure_log.append({"row": idx, "error": "JSONDecodeError", "text": response_text})
            skipped_count += 1
        except Exception as e:
            print(f"❌ Error running ollama at row {idx}: {e}")
            failure_log.append({"row": idx, "error": str(e), "prompt": prompt})
            skipped_count += 1

    # Save Cleaned Results
    cleaned_df = pd.DataFrame(results)
    cleaned_df.to_csv(cleaned_file, index=False)
    print(f"✅ Cleaned data saved: {cleaned_file}")
    print(f"📊 Stats for {raw_file.name}:")
    print(f"    Total rows: {len(df)}")
    print(f"    Cleaned entries: {len(results)}")
    print(f"    Skipped/Errors: {skipped_count}")

    if failure_log:
        error_path = cleaned_file.with_suffix(".error_log.json")
        with open(error_path, "w") as f:
            json.dump(failure_log, f, indent=2)
        print(f"🛠️ Error log saved to: {error_path}")

print("🎉 All unprocessed files cleaned and saved successfully.")
