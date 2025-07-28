# This file contains Helpers: fetch_posts, process_comments

import praw
from .config import headers
from datetime import datetime

# We will remove this function cause github workflow needs an authenticated coummunication
# def fetch_posts(subreddit, after=None):
#     try:
#         response = httpx.get(
#             f'https://www.reddit.com/r/{subreddit}/new.json',
#             headers=headers,
#             params={'limit': 100, 'after': after, 't': 'week'}
#         )
#         response.raise_for_status()
#         return response.json()['data']
#     except Exception as e:
#         print(f"Error fetching posts from r/{subreddit}: {e}")
#         return None

def fetch_posts_with_praw(reddit, subreddit_name, limit=100):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        return list(subreddit.new(limit=limit))
    except Exception as e:
        print(f"Error fetching posts from r/{subreddit_name}: {e}")
        return []


def process_comments(submission, counters):
    try:
        submission.comments.replace_more(limit=0)
        valid_comments = []

        for comment in submission.comments[:3]:
            if any(bot_phrase in comment.body for bot_phrase in [
                "Thanks for posting", "I am a bot", "Please read the rules"
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
