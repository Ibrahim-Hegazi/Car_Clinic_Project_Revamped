import os
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from datetime import datetime
import argparse

# ========= CONFIG ==========
RAW_DATA_PATH = Path("data/raw/")
CLEANED_DATA_PATH = Path("data/cleaned/")
MODEL_NAME = "deepseek-ai/deepseek-coder-6.7b-instruct"  # Change for offline model
USE_OFFLINE_MODEL = False  # Set to True if model is local
MAX_INPUT_LEN = 1024  # truncate prompt


# ===========================

# Load LLM
def load_model():
    if USE_OFFLINE_MODEL:
        print("🔁 Loading offline model...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            torch_dtype="auto",
            device_map="auto"
        )
        return lambda prompt: model_generate(prompt, tokenizer, model)
    else:
        print("🌐 Using Hugging Face Inference Pipeline...")
        return pipeline("text-generation", model=MODEL_NAME, max_new_tokens=256)


def model_generate(prompt, tokenizer, model):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_INPUT_LEN)
    outputs = model.generate(**inputs, max_new_tokens=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# Clean input (trimming, punctuation normalization, etc.)
def prepare_input(row: pd.Series) -> str:
    title = row.get("title", "")
    text = row.get("selftext", "")
    comment = row.get("top_comment", "")

    # Prompt Template
    prompt = (
        "Given a Reddit post title, selftext, and top comment, extract the problem and solution.\n"
        f"Title: {title}\n"
        f"Selftext: {text}\n"
        f"Top Comment: {comment}\n"
        "Return a JSON object like: {\"problem\": \"...\", \"solution\": \"...\"}"
    )
    return prompt[:MAX_INPUT_LEN]


# Clean LLM output
def extract_json(response: str) -> Optional[Dict[str, str]]:
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        content = response[start:end]
        parsed = json.loads(content)
        if "problem" in parsed and "solution" in parsed:
            return parsed
    except Exception:
        pass
    return None


# Load latest CSV file
def get_latest_raw_csv() -> Path:
    csv_files = sorted(RAW_DATA_PATH.glob("*.csv"), key=os.path.getmtime, reverse=True)
    return csv_files[0] if csv_files else None


# Save results
def save_output(results: List[Dict], raw_name: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    out_json = CLEANED_DATA_PATH / f"{raw_name}_cleaned_{timestamp}.jsonl"
    out_csv = CLEANED_DATA_PATH / f"{raw_name}_cleaned_{timestamp}.csv"

    # JSONL
    with open(out_json, "w", encoding="utf-8") as f:
        for item in results:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # CSV
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"✅ Saved {len(results)} cleaned rows to:")
    print(f"   • {out_json}")
    print(f"   • {out_csv}")


# Main
def main(input_file: Optional[str] = None):
    CLEANED_DATA_PATH.mkdir(parents=True, exist_ok=True)

    if input_file:
        data_path = Path(input_file)
    else:
        data_path = get_latest_raw_csv()
        if data_path is None:
            print("❌ No raw CSV file found.")
            return

    print(f"📄 Loading data from: {data_path}")
    df = pd.read_csv(data_path).fillna("")

    model = load_model()
    cleaned = []

    for idx, row in df.iterrows():
        prompt = prepare_input(row)
        try:
            raw_output = model(prompt) if not USE_OFFLINE_MODEL else model(prompt)
            response_text = raw_output[0]["generated_text"] if isinstance(raw_output, list) else raw_output
            parsed = extract_json(response_text)
            if parsed:
                cleaned.append({
                    "title": row["title"],
                    "problem": parsed["problem"],
                    "solution": parsed["solution"]
                })
            else:
                print(f"⚠️ [{idx}] Failed to parse response:\n{response_text}")
        except Exception as e:
            print(f"❌ [{idx}] Error: {e}")
            continue

    raw_name = data_path.stem.replace(".csv", "")
    save_output(cleaned, raw_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="C:\\Users\\Ibrahim_Hegazi\\Desktop\\Eagles\\Car_Clinic_Project\\data\\raw\\Reddit_CarAdvice_2025-07-29.csv")
    args = parser.parse_args()

    main(args.file)
