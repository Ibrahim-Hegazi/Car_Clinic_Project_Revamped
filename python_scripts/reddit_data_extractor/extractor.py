import httpx
import pandas as pd
import time
import os
from datetime import datetime, timedelta
import praw
from pathlib import Path


def extract_reddit_data():
    start_time = time.time()

    # ---------- METRICS COUNTERS ----------
    counters = {
        'total_posts_fetched': 0,
        'posts_filtered_time': 0,
        'posts_filtered_comments': 0,
        'comments_skipped': 0,
        'valid_posts_stored': 0
    }

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
        # client_id='rRsSEn42kJ-qRpPeAGwAWQ',
        # client_secret='iSAoAUQvfOCkJMZBLkBO7CPCxe8TAA',
        # user_agent='User-Agent: script:MyDataScraperForLLM:3.0 (by /u/Many-Refuse5176)'
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        user_agent=os.environ['REDDIT_USER_AGENT']
    )

    # Headers for JSON API
    headers = {
        'User-Agent': 'MyRedditScraper/2.0 (by /u/YOUR_USERNAME)'
    }

    # Date setup
    yesterday = datetime.utcnow() - timedelta(days=1)
    start_timestamp = int(yesterday.replace(hour=0, minute=0, second=0).timestamp())
    end_timestamp = int(yesterday.replace(hour=23, minute=59, second=59).timestamp())

    # ---------- SCRAPING HELPERS ----------
    def fetch_posts(subreddit, after=None):
        params = {
            'limit': POST_LIMIT_PER_PAGE,
            'after': after,
            't': 'week'
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
        try:
            submission.comments.replace_more(limit=0)
            valid_comments = []
            for comment in submission.comments[:3]:
                if any(phrase in comment.body for phrase in [
                    "Thanks for posting",
                    "I am a bot",
                    "Please read the rules"
                ]):
                    counters['comments_skipped'] += 1
                    continue

                valid_comments.append({
                    'comment_id': comment.id,
                    'comment_body': comment.body,
                    'comment_score': comment.score,
                    'comment_author': str(comment.author)
                })

            return valid_comments
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
            data = fetch_posts(subreddit, after)
            if not data:
                break

            for post in data['children']:
                counters['total_posts_fetched'] += 1
                if post_count >= MAX_POSTS_PER_SUBREDDIT:
                    break

                post_data = post['data']

                if not (start_timestamp <= post_data['created_utc'] <= end_timestamp):
                    counters['posts_filtered_time'] += 1
                    continue
                if post_data['num_comments'] == 0:
                    counters['posts_filtered_comments'] += 1
                    continue

                try:
                    submission = reddit.submission(id=post_data['id'])
                    comments = process_comments(submission)

                    if comments:
                        post_entry = {
                            'id': post_data['id'],
                            'title': post_data['title'],
                            'selftext': post_data['selftext'],
                            'score': post_data['score'],
                            'created_utc': post_data['created_utc'],
                            'num_comments': post_data['num_comments'],
                            'subreddit': subreddit,
                            'top_comments': comments
                        }

                        all_posts.append(post_entry)
                        post_count += 1
                        counters['valid_posts_stored'] += 1

                        if post_count % 10 == 0:
                            print(f"Collected {post_count} posts from r/{subreddit}")

                except Exception as e:
                    print(f"Error processing post {post_data['id']}: {e}")
                    continue

            after = data['after']
            if not after:
                print(f"No more posts in r/{subreddit} (got {post_count}/{MAX_POSTS_PER_SUBREDDIT})")
                break

            time.sleep(3)

    # ---------- DATA SAVING ----------
    if all_posts:
        scraping_time_unix = int(time.time())

        for post in all_posts:
            post['top_comments'] = "\n\n".join(
                f"{c['comment_author']} (Score: {c['comment_score']}): {c['comment_body']}"
                for c in post['top_comments']
            )
            post['scraping_time_utc'] = scraping_time_unix

        df = pd.DataFrame(all_posts)
        df['created_datetime_utc'] = pd.to_datetime(df['created_utc'], unit='s')
        df['scraping_datetime_utc'] = pd.to_datetime(df['scraping_time_utc'], unit='s')

        base_columns = [col for col in df.columns if col != 'top_comments']
        column_order = base_columns + ['top_comments']
        df = df[column_order]

        if os.path.exists(CSV_FILE):
            existing_df = pd.read_csv(CSV_FILE)
            existing_df = existing_df[column_order] if 'top_comments' in existing_df.columns else existing_df
            df = pd.concat([existing_df, df]).drop_duplicates('id', keep='last')

        df.to_csv(CSV_FILE, index=False)
        print(f"\nSaved {len(df)} posts to {CSV_FILE}")

        print("\n=== Collection Summary ===")
        print("Posts by subreddit:")
        print(df['subreddit'].value_counts())
    else:
        print("\nNo posts collected.")

    # ---------- METRICS REPORT ----------
    print("\n=== Debugging Counters ===")
    for key, value in counters.items():
        print(f"{key}: {value}")

    # ---------- EXECUTION TIME ----------
    execution_time = (time.time() - start_time) / 60
    print(f"\nCompleted in {execution_time:.2f} minutes")


if __name__ == "__main__":
    extract_reddit_data()
