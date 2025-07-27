# This file Contains the PRAW setup

import praw

def get_reddit_client():
    return praw.Reddit(
        client_id='rRsSEn42kJ-qRpPeAGwAWQ',
        client_secret='iSAoAUQvfOCkJMZBLkBO7CPCxe8TAA',
        user_agent='script:MyDataScraperForLLM:3.0 (by /u/Many-Refuse5176)'
    )
