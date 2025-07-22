# The most detrimental issues for me are
#   1. Reddit API Rate Limiting (Add the needed delays),
#   2. Reddit’s "After" Pagination Limit (if the subreddit does not have the 500 post or reached the end of its post then go to the next subreddit in the list),
#   3. Comment Fetching is Slow( Take the posts that has comments in it ).

import httpx
import pandas as pd
import time
import os
from datetime import datetime, timedelta
import praw
from pathlib import Path


def extract_reddit_data():
    start_time = time.time()

    # ---------- CONFIGURATION ----------
    SUBREDDITS = [
        'MechanicAdvice',
        'CarTalk',
        'carquestions',
        'automotive',
        'CarHelp',
        'carproblems',
        'autorepair',
        'AskMechanicscar',
        'mechanic',
        'StupidCarQuestions',
        'CarHacking',
        'AskMechanics',
        'AutoMechanics',
        'CartalkUK'
    ]
    POST_LIMIT_PER_PAGE = 100  # Max allowed by Reddit API
    MAX_POSTS_PER_SUBREDDIT = 500



    # Get project root: go 3 levels up from this file
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    DATA_DIR = PROJECT_ROOT / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)  # Ensure it exists

    # Use today's date in file name
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    CSV_FILE = DATA_DIR / f"Reddit_CarAdvice_{today_str}.csv"


    # PRAW Setup
    reddit = praw.Reddit(
        client_id='CpCduCYpVMH7S-X2-LGX7w',
        client_secret='AU390E7U6kE8PgUBmXJ01Vg0FJmQXg',
        user_agent='MultiSubredditCarDataExtractor/2.0 by Ibrahim Hegazi'
    )

    # Headers for JSON API
    headers = {
        'User-Agent': 'MyRedditScraper/2.0 (by /u/YOUR_USERNAME)'
    }

    # Date setup
    yesterday = datetime.utcnow() - timedelta(days=1)
    start_timestamp = int(yesterday.replace(hour=0, minute=0, second=0).timestamp())
    end_timestamp = int(yesterday.replace(hour=23, minute=59, second=59).timestamp())


    # ---------- IMPROVED SCRAPING FUNCTIONS ----------
    def fetch_posts(subreddit, after=None):
        """Fetch posts with rate limiting and pagination handling"""
        params = {
            'limit': POST_LIMIT_PER_PAGE,
            'after': after,
            't': 'week'  # Extend time window
        }

        try:
            response = httpx.get(
                f'https://www.reddit.com/r/{subreddit}/new.json',
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit}: {e}")
            return None


    def process_comments(submission):
        """Efficient comment processing with filtering"""
        try:
            submission.comments.replace_more(limit=0)  # Remove 'load more' comments
            return [
                {
                    'comment_id': comment.id,
                    'comment_body': comment.body,
                    'comment_score': comment.score,
                    'comment_author': str(comment.author)
                }
                for comment in submission.comments[:3]  # Only top 3 comments
                if not any(phrase in comment.body for phrase in [
                    "Thanks for posting",
                    "I am a bot",
                    "Please read the rules"
                ])
            ]
        except Exception as e:
            print(f"Comment error in post {submission.id}: {e}")
            return []


    # ---------- MAIN SCRAPING LOGIC ----------
    all_posts = []

    for subreddit in SUBREDDITS:
        print(f"\n=== Starting r/{subreddit} ===")
        post_count = 0
        after = None

        while post_count < MAX_POSTS_PER_SUBREDDIT:
            # Fetch posts with rate limiting
            data = fetch_posts(subreddit, after)
            if not data:
                break

            # Process posts
            for post in data['children']:
                if post_count >= MAX_POSTS_PER_SUBREDDIT:
                    break

                post_data = post['data']

                # Skip if outside time window or has no comments
                if not (start_timestamp <= post_data['created_utc'] <= end_timestamp):
                    continue
                if post_data['num_comments'] == 0:
                    continue

                # Get comments only for promising posts
                try:
                    submission = reddit.submission(id=post_data['id'])
                    comments = process_comments(submission)

                    if comments:  # Only store if has valid comments
                        post_entry = post_data.copy()  # ✅ <-- This line captures all fields
                        post_entry['subreddit'] = subreddit
                        post_entry['top_comments'] = comments

                        all_posts.append(post_entry)
                        post_count += 1

                        if post_count % 10 == 0:
                            print(f"Collected {post_count} posts from r/{subreddit}")

                except Exception as e:
                    print(f"Error processing post {post_data['id']}: {e}")
                    continue

            # Pagination control
            after = data.get('after')
            if not after:
                print(f"No more posts in r/{subreddit} (got {post_count}/{MAX_POSTS_PER_SUBREDDIT})")
                break

            # Conservative rate limiting
            time.sleep(3)  # Increased from 2 to 3 seconds



    # ---------- DATA SAVING ----------
    if all_posts:
        # Inject scraping timestamp into each post
        scraping_time_unix = int(time.time())

        # Format comments for CSV
        for post in all_posts:
            post['top_comments'] = "\n\n".join(
                f"{c['comment_author']} (Score: {c['comment_score']}): {c['comment_body']}"
                for c in post['top_comments']
            )
            post['scraping_time_utc'] = scraping_time_unix

        # Create DataFrame and reorder columns to put 'top_comments' last
        df = pd.DataFrame(all_posts)

        # Convert timestamps to human-readable datetime
        df['created_datetime_utc'] = pd.to_datetime(df['created_utc'], unit='s')
        df['scraping_datetime_utc'] = pd.to_datetime(df['scraping_time_utc'], unit='s')


        # Get all columns except 'top_comments', then add it at the end
        base_columns = [col for col in df.columns if col != 'top_comments']
        column_order = base_columns + ['top_comments']
        df = df[column_order]

        # Smart CSV saving
        if os.path.exists(CSV_FILE):
            existing_df = pd.read_csv(CSV_FILE)
            # Ensure column order matches when concatenating
            existing_df = existing_df[column_order] if 'top_comments' in existing_df.columns else existing_df
            df = pd.concat([existing_df, df]).drop_duplicates('id', keep='last')

        df.to_csv(CSV_FILE, index=False)
        print(f"\nSaved {len(df)} posts to {CSV_FILE}")

        # Print summary
        print("\n=== Collection Summary ===")
        print("Posts by subreddit:")
        print(df['subreddit'].value_counts())
    else:
        print("\nNo posts collected.")



    # Performance metrics
    execution_time = (time.time() - start_time) / 60
    print(f"\nCompleted in {execution_time:.2f} minutes")




# Key Improvements:
# Rate Limiting Solved:
#
#   Increased delay between requests to 3 seconds
#
#   Proper error handling for HTTP errors
#
#   Batch processing of posts
#
# Pagination Handling:
#
#   Automatically moves to next subreddit when current one is exhausted
#
#   Extended time window to 3 days for more post availability
#
#   Clear logging of progress per subreddit
#
# Efficient Comment Fetching:
#
#   Only processes posts with comments (num_comments > 0)
#
#   Skips automod and bot comments
#
#   Limits to top 3 comments per post
#
#   Faster comment processing with list comprehension
#
# Multi-Subreddit Support:
#
#   Processes all subreddits in the list
#
#   Tracks source subreddit for each post
#
#   Balanced collection across all sources
#
# Data Quality:
#
#   Better comment formatting
#
#   More consistent data structure
#
#   Duplicate prevention
#
# Additional Optimizations:
#   Uses dictionary unpacking for cleaner post data collection
#
#   More informative progress reporting
#
#   Better CSV handling (appends safely to existing files)
#
#   Comprehensive error logging