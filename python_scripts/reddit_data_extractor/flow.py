# The starting point of our code

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta
import logging
from .scraper import extract_reddit_data
# from extractor import extract_reddit_data



import sys
from pathlib import Path
# Add python_scripts/ to the path
CURRENT_DIR = Path(__file__).resolve()
PYTHON_SCRIPTS_DIR = CURRENT_DIR.parents[1]
sys.path.append(str(PYTHON_SCRIPTS_DIR))

@task(
    name="Extract Reddit Data",
    retries=3,
    retry_delay_seconds=60,
    #cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
    timeout_seconds=3600  # fail if runs longer than 30 minutes
)
def extract_task():
    logger = get_run_logger()
    logger.info("🔁 Starting Reddit data extraction...")
    extract_reddit_data()
    logger.info("✅ Finished Reddit data extraction.")

@flow(name="Reddit Pipeline")
def reddit_pipeline():
    extract_task()

if __name__ == "__main__":
    reddit_pipeline()
