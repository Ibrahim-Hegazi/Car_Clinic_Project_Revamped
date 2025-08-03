# This file contains Configs like subreddit list, limits, API credentials

from datetime import datetime, timedelta
from pathlib import Path

SUBREDDITS = [
    'MechanicAdvice', 'CarTalk', 'carquestions', 'automotive', 'CarHelp',
    'carproblems', 'autorepair', 'AskMechanicscar', 'mechanic',
    'StupidCarQuestions', 'CarHacking', 'AskMechanics', 'AutoMechanics', 'CartalkUK'
]

POST_LIMIT_PER_PAGE = 50
MAX_POSTS_PER_SUBREDDIT = 50

headers = {
    'User-Agent': 'MyRedditScraper/2.0 (by /u/YOUR_USERNAME)'
}

yesterday = datetime.utcnow() - timedelta(days=1)
START_TIMESTAMP = int(yesterday.replace(hour=0, minute=0, second=0).timestamp())
END_TIMESTAMP = int(yesterday.replace(hour=23, minute=59, second=59).timestamp())

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
# CSV_FILE = DATA_DIR / f"Reddit_CarAdvice_{datetime.utcnow().strftime('%Y-%m-%d')}.csv" # outdated subdirectory

RAW_DATA_DIR = DATA_DIR / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE = RAW_DATA_DIR / f"Reddit_CarAdvice_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"
