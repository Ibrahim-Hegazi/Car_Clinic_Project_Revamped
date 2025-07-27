# This file contains CSV and data saving logic

import pandas as pd
import time
import os

def save_data(all_posts, counters, CSV_FILE):
    if not all_posts:
        print("No posts collected.")
        return

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
    print("Posts by subreddit:")
    print(df['subreddit'].value_counts())
