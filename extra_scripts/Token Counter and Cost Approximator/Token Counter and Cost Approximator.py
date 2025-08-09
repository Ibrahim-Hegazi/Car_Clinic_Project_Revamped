# 📁 Car_Clinic_Project/extra_scripts/Token Counter and Cost Approximator/Token Counter and Cost Approximator.py

import pandas as pd
import tiktoken
from pathlib import Path
from datetime import datetime

# === Config === #
MODEL_NAME = "gpt-4"
COST_PER_1K_TOKENS = 0.03  # Adjust this for your model
RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

# Add this to the top with your other imports
today_str = datetime.today().strftime("%Y-%m-%d")

OUTPUT_FILE = Path(__file__).resolve().parent / f"token_cost_summary_{today_str}.csv"

# === Load tokenizer === #
enc = tiktoken.encoding_for_model(MODEL_NAME)

def count_tokens(text: str) -> int:
    """Tokenize using tiktoken and return token count."""
    if not isinstance(text, str):
        return 0
    try:
        return len(enc.encode(text))
    except Exception:
        return 0

def process_file(file_path: Path) -> dict:
    """Process a single CSV and return stats."""
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Failed to read {file_path.name}: {e}")
        return None

    # Combine fields
    df['combined_text'] = df['title'].fillna('') + ' ' + df['selftext'].fillna('') + ' ' + df['top_comments'].fillna('')

    # Token count
    df['token_count'] = df['combined_text'].apply(count_tokens)

    total_tokens = df['token_count'].sum()
    estimated_cost = (total_tokens / 1000) * COST_PER_1K_TOKENS

    return {
        "file_name": file_path.name,
        "total_posts": len(df),
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(estimated_cost, 4)
    }

def main():
    summary = []
    total_cost = 0.0

    print(f"🔍 Scanning directory: {RAW_DATA_DIR}")
    csv_files = list(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("⚠️ No CSV files found.")
        return

    for file in csv_files:
        print(f"📄 Processing: {file.name}")
        stats = process_file(file)
        if stats:
            summary.append(stats)
            total_cost += stats['estimated_cost_usd']

    # Save results
    df_summary = pd.DataFrame(summary)
    df_summary = df_summary.sort_values(by='estimated_cost_usd', ascending=False)

    df_summary.loc["TOTAL"] = ["All Files", "", df_summary["total_tokens"].sum(), round(total_cost, 4)]
    df_summary.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ Summary saved to: {OUTPUT_FILE}")
    print(f"💰 Total estimated cost: ${round(total_cost, 4)} USD")

if __name__ == "__main__":
    main()
