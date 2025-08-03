# reddit_data_cleaner/flow.py
from prefect import flow, get_run_logger
from reddit_data_cleaner.cleaner import run_llm_cleaning_logic  # Absolute import

@flow(name="Reddit LLM Cleaning Flow")
def reddit_llm_flow():
    logger = get_run_logger()
    run_llm_cleaning_logic(logger)

if __name__ == "__main__":
    reddit_llm_flow()
