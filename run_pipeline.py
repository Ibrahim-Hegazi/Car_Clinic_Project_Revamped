# run_pipeline.py – Launch script for GitHub Actions or manual run

from python_scripts.reddit_data_extractor.flow import reddit_pipeline
from python_scripts.reddit_data_cleaner.flow import reddit_llm_flow

if __name__ == "__main__":
    print("🚀 Starting Reddit data extraction...")
    reddit_pipeline()

    print("\n🧠 Starting Reddit LLM cleaning...")
    reddit_llm_flow()
