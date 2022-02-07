from django.conf import settings


SOCIAL_AUTH_TWITTER_KEY = settings.TWITTER_CONSUMER_KEY
SOCIAL_AUTH_TWITTER_SECRET = settings.TWITTER_CONSUMER_SECRET
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/home/'
SOCIAL_AUTH_LOGIN_URL = 'login/'
