import os

# DJANGO APPLICATION CONFIGS VARIABLES
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = os.environ.get("APP_SECRET_KEY")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(" ")


# CUSTOM DJANGO APPLICATION CONFIGS VARIABLES
APP_ENV = os.environ.get("APP_ENV")
APP_URL = os.environ.get("APP_URL")


# REDIS
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_URI = os.environ.get('REDIS_URI')


# MYSQL DATABASE
DB_NAME = os.environ.get('DB_NAME'),
DB_USERNAME = os.environ.get('DB_USERNAME'),
DB_PASSWORD = os.environ.get('DB_PASSWORD'),
DB_HOST = os.environ.get('DB_HOST'),
DB_PORT = os.environ.get('DB_PORT'),

# TWITTER SECRETS
TWITTER_SECRETS = {
    "consumer_key": os.environ.get("TWITTER_CONSUMER_KEY"),
    "consumer_secret": os.environ.get("TWITTER_CONSUMER_SECRET"),
    "access_token": os.environ.get("TWITTER_ACCESS_TOKEN"),
    "access_token_secret": os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
}

# DJANGO SOCIAL AUTH CONFIGS
SOCIAL_AUTH_TWITTER_KEY = TWITTER_SECRETS['consumer_key']
SOCIAL_AUTH_TWITTER_SECRET = TWITTER_SECRETS['consumer_secret']
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/home/'
SOCIAL_AUTH_LOGIN_URL = 'login/'
