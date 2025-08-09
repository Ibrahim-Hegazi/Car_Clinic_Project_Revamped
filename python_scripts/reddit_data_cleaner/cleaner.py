# # reddit_data_cleaner/cleaner.py
# # Acts as the main script and entry point. It imports from other modules and executes the cleaning loop.
import pandas as pd
import time
import logging
from utils import get_paths, load_raw_data, should_skip_cleaning, save_cleaned_data
from llm_runner import clean_single_row

def run_llm_cleaning_logic(logger=None):
    if logger is None:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("LLM Cleaner")

    raw_dir, cleaned_dir, raw_file, cleaned_file = get_paths()

    if not raw_dir.exists():
        logger.error(f"❌ RAW data directory not found: {raw_dir}")
        return

    cleaned_dir.mkdir(parents=True, exist_ok=True)

    if should_skip_cleaning(cleaned_file, logger):
        return

    df = load_raw_data(raw_file, logger)
    if df is None:
        return

    logger.info(f"✅ Loaded {len(df)} rows from raw data.")
    results, failure_log = [], []
    skipped_count = 0
    start_time = time.time()

    for idx, row in df.head(5).iterrows():
        result, error = clean_single_row(row, idx, logger)
        if result:
            results.append(result)
        elif error:
            failure_log.append(error)
            skipped_count += 1
        else:
            skipped_count += 1

    cleaned_df = pd.DataFrame(results)

    if 'post_id' in cleaned_df.columns:
        columns = ['post_id'] + [col for col in cleaned_df.columns if col != 'post_id']
        cleaned_df = cleaned_df[columns]

    save_cleaned_data(cleaned_df, cleaned_file, failure_log, logger)

    logger.info("📊 Stats:")
    logger.info(f" Total rows: {len(df)}")
    logger.info(f" Cleaned entries: {len(results)}")
    logger.info(f" Skipped/Errors: {skipped_count}")
    logger.info(f"🕒 Total cleaning time: {time.time() - start_time:.2f} seconds")
    logger.info("🎉 Cleaning completed.")
