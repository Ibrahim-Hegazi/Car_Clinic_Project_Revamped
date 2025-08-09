# Handles general-purpose utilities and filesystem logic.
from pathlib import Path
from datetime import datetime
import pandas as pd
import json

def get_paths():
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "data" / "raw"
    cleaned_dir = project_root / "data" / "cleaned"
    today_str = datetime.now().strftime("%Y-%m-%d")
    raw_file = raw_dir / f"Reddit_CarAdvice_{today_str}.csv"
    cleaned_file = cleaned_dir / f"Reddit_CarAdvice_Cleaned_{today_str}.csv"
    return raw_dir, cleaned_dir, raw_file, cleaned_file


def load_raw_data(raw_file: Path, logger):
    if not raw_file.exists():
        logger.warning("⏭️ Today's raw file not found. Skipping cleaning.")
        return None
    logger.info(f"📥 Reading raw CSV: {raw_file}")
    return pd.read_csv(raw_file)

def should_skip_cleaning(cleaned_file: Path, logger) -> bool:
    if cleaned_file.exists():
        logger.info("✅ Already cleaned today’s file.")
        return True
    return False

def save_cleaned_data(cleaned_df: pd.DataFrame, cleaned_file: Path, failure_log: list, logger):
    try:
        cleaned_df.to_csv(cleaned_file, index=False)
        logger.info(f"✅ Cleaned data saved successfully: {cleaned_file}")
    except Exception as e:
        logger.error(f"❌ Failed to save cleaned data: {e}")
        return

    if failure_log:
        error_path = cleaned_file.with_suffix(".error_log.json")
        with open(error_path, "w") as f:
            json.dump(failure_log, f, indent=2)
        logger.warning(f"🛠️ Error log saved to: {error_path}")

# DONEEEEEEEEE