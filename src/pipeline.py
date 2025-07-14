import os
from dotenv import load_dotenv

from src.extract.linkedin_scraper import LinkedInScraper
from src.extract.twitter_scraper import TwitterScraper
from src.transform.clean_data import (
    transform_linkedin_data,
    transform_twitter_data,
    combine_platform_data
)
from src.load.database import PostManager

load_dotenv()

def run_etl():

    LINKEDIN_USER = os.getenv('LINKEDIN_USER')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    TWITTER_EMAIL = os.getenv('TWITTER_EMAIL')
    TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')
    TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
    DB_URL = os.getenv('DB_URL')

    db = PostManager(DB_URL)

    db.init_db()

    linkedin_scraper = LinkedInScraper(email=LINKEDIN_USER, password=LINKEDIN_PASSWORD)
    linkedin_scraper._login()

    twitter_scraper = TwitterScraper(email=TWITTER_EMAIL, password=TWITTER_PASSWORD, username=TWITTER_USERNAME)
    twitter_scraper._login()

    linkedin_data = []
    twitter_data = []

    topics = []

    for topic in topics:
        linkedin_posts = linkedin_scraper.get_relevant_posts(search_query=topic)
        linkedin_data.extend(linkedin_posts)

        twitter_posts = twitter_scraper.get_relevant_posts(search_query=topic, recent=True)
        twitter_posts.extend(twitter_scraper.get_relevant_posts(search_query=topic, recent=False))
        twitter_data.extend(twitter_posts)

    linkedin_scraper.close_driver()
    twitter_scraper.close_driver()

    linkedin_df = transform_linkedin_data(linkedin_data)
    twitter_df = transform_twitter_data(twitter_data)
    combined_df = combine_platform_data(linkedin_df, twitter_df)

    db.save_to_db(combined_df)

