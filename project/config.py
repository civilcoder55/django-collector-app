import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, '.env'))

APP_ENV = os.getenv("APP_ENV")
SECRET_KEY = os.getenv("APP_SECRET_KEY")
APP_URL = os.getenv("APP_URL")

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

TWITTER_SECRETS = {
    "consumer_key": os.getenv("TWITTER_CONSUMER_KEY"),
    "consumer_secret": os.getenv("TWITTER_CONSUMER_SECRET"),
    "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
}

SOCIAL_AUTH_TWITTER_KEY = TWITTER_SECRETS['CONSUMER_KEY']
SOCIAL_AUTH_TWITTER_SECRET = TWITTER_SECRETS['CONSUMER_SECRET']
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/home/'
SOCIAL_AUTH_LOGIN_URL = 'login/'
