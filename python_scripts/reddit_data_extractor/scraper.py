# scraper.py — Main logic (loops, counters)

import time
import logging
import pandas as pd
import os
from .config import *
from .reddit_client import get_reddit_client
from .utils import fetch_posts_with_praw, process_comments
from .writer import save_data
from prefect import get_run_logger

# Setup module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Optional: configure a basic console handler if running standalone
if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def extract_reddit_data():
    start_time = time.time()
    reddit = get_reddit_client()

    counters = {
        'total_posts_fetched': 0,
        'posts_filtered_time': 0,
        'posts_filtered_comments': 0,
        'comments_skipped': 0,
        'valid_posts_stored': 0
    }

    all_posts = []

    for subreddit in SUBREDDITS:
        # print(f"\n=== Starting r/{subreddit} ===")
        logger.info(f"=== Starting r/{subreddit} ===")
        post_count = 0

        posts = fetch_posts_with_praw(reddit, subreddit, limit=MAX_POSTS_PER_SUBREDDIT)

        for submission in posts:
            counters['total_posts_fetched'] += 1

            if post_count >= MAX_POSTS_PER_SUBREDDIT:
                break

            if not (START_TIMESTAMP <= submission.created_utc <= END_TIMESTAMP):
                counters['posts_filtered_time'] += 1
                continue
            if submission.num_comments == 0:
                counters['posts_filtered_comments'] += 1
                continue

            try:
                comments = process_comments(submission, counters)

                if comments:
                    post_entry = {
                        'id': submission.id,
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'score': submission.score,
                        'created_utc': submission.created_utc,
                        'num_comments': submission.num_comments,
                        'subreddit': subreddit,
                        'top_comments': comments
                    }

                    all_posts.append(post_entry)
                    post_count += 1
                    counters['valid_posts_stored'] += 1

                    if post_count % 10 == 0:
                        print(f"Collected {post_count} posts from r/{subreddit}")
                        logger.info(f"Collected {post_count} posts from r/{subreddit} ===")

            except Exception as e:
                # print(f"Error processing post {submission.id}: {e}")
                logger.info(f"Error processing post {submission.id}: {e} ===")
                continue

            time.sleep(3)

    save_data(all_posts, counters, CSV_FILE)

    # print("\n=== Debugging Counters ===")
    logger.info("\n=== Debugging Counters ===")
    for key, value in counters.items():
        # print(f"{key}: {value}")
        logger.info(f"{key}: {value}")

    # print(f"\nCompleted in {(time.time() - start_time) / 60:.2f} minutes")
    logger.info(f"\nCompleted in {(time.time() - start_time) / 60:.2f} minutes")
