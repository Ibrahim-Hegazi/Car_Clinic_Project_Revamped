"""
reddit_data_extractor - A modular package for extracting car-related data from Reddit.

This package contains:
- config.py: Subreddit list, date ranges, API limits, and file paths
- reddit_client.py: Reddit PRAW API setup
- utils.py: Helpers for fetching posts and filtering comments
- scraper.py: Main logic for orchestrating data extraction
- writer.py: Writes extracted post data to CSV
- flow.py: Prefect flow to orchestrate the extraction pipeline
"""

from .scraper import extract_reddit_data
from .flow import reddit_pipeline

__version__ = "1.0.0"
__all__ = ['extract_reddit_data', 'reddit_pipeline']
