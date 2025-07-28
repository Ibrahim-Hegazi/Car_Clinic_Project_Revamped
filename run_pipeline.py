# run_pipeline.py – Launch script for GitHub Actions or manual run

from python_scripts.reddit_data_extractor.flow import reddit_pipeline

if __name__ == "__main__":
    reddit_pipeline()
