# reddit_data_cleaner/flow.py

from prefect import flow, get_run_logger, task
from prefect.tasks import task_input_hash
from datetime import timedelta
import sys
from pathlib import Path
import logging

# Add python_scripts/ to the path so relative imports work
CURRENT_DIR = Path(__file__).resolve()
PYTHON_SCRIPTS_DIR = CURRENT_DIR.parents[1]
sys.path.append(str(PYTHON_SCRIPTS_DIR))

# Now we can safely import cleaner logic
from cleaner import run_llm_cleaning_logic


@task(
    name="Run LLM Cleaning Logic",
    retries=2,
    retry_delay_seconds=30,
    # cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
    timeout_seconds=14400 # 4 hours
)
def llm_cleaning_task():
    logger = get_run_logger()
    logger.info("🧹 Starting LLM cleaning logic...")
    run_llm_cleaning_logic(logger)
    logger.info("✅ Finished LLM cleaning.")

@flow(name="Reddit LLM Cleaning Flow")
def reddit_llm_flow():
    llm_cleaning_task()

if __name__ == "__main__":
    reddit_llm_flow()
