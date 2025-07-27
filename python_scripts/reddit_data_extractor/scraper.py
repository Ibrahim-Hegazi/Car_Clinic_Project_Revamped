# This file Main logic (loops, counters)

import time
import pandas as pd
import os
from config import *
from reddit_client import get_reddit_client
from utils import fetch_posts, process_comments
from writer import save_data

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
        print(f"\n=== Starting r/{subreddit} ===")
        post_count = 0
        after = None

        while post_count < MAX_POSTS_PER_SUBREDDIT:
            data = fetch_posts(subreddit, after)
            if not data: break

            for post in data['children']:
                counters['total_posts_fetched'] += 1
                if post_count >= MAX_POSTS_PER_SUBREDDIT:
                    break

                post_data = post['data']
                if not (START_TIMESTAMP <= post_data['created_utc'] <= END_TIMESTAMP):
                    counters['posts_filtered_time'] += 1
                    continue
                if post_data['num_comments'] == 0:
                    counters['posts_filtered_comments'] += 1
                    continue

                try:
                    submission = reddit.submission(id=post_data['id'])
                    comments = process_comments(submission, counters)
                    if comments:
                        all_posts.append({
                            'id': post_data['id'],
                            'title': post_data['title'],
                            'selftext': post_data['selftext'],
                            'score': post_data['score'],
                            'created_utc': post_data['created_utc'],
                            'num_comments': post_data['num_comments'],
                            'subreddit': subreddit,
                            'top_comments': comments
                        })
                        post_count += 1
                        counters['valid_posts_stored'] += 1

                        if post_count % 10 == 0:
                            print(f"Collected {post_count} posts from r/{subreddit}")
                except Exception as e:
                    print(f"Error processing post {post_data['id']}: {e}")
                    continue

            after = data.get('after')
            if not after:
                print(f"No more posts in r/{subreddit} (got {post_count}/{MAX_POSTS_PER_SUBREDDIT})")
                break

            time.sleep(3)

    save_data(all_posts, counters, CSV_FILE)
    print("\n=== Debugging Counters ===")
    for key, value in counters.items():
        print(f"{key}: {value}")

    print(f"\nCompleted in {(time.time() - start_time) / 60:.2f} minutes")
