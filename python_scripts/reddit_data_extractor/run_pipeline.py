# run_pipeline.py – Launch script for GitHub Actions or manual run

from .flow import reddit_pipeline

if __name__ == "__main__":
    reddit_pipeline()
