

import requests
import tweepy
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.urls import reverse
from posts.models import Post
from social_django.models import UserSocialAuth
from utils.logger import logger

from .cleaner import Cleaner
from .grabber import Grabber


class Handler:

    auth = tweepy.OAuthHandler(**settings.TWITTER_SECRETS)
    tweepy_client = tweepy.API(auth)

    @classmethod
    def handle_collection(cls, status):
        try:
            post = Post.objects.filter(
                id=status.in_reply_to_status_id).first()
            if post:
                cls.__add_post_to_user(
                    post=post, user_id=status.user.id_str)
                cls.__reply_to_status(status=status, old=True)

            else:
                id = status.in_reply_to_status_id
                thread = cls.tweepy_client.get_status(
                    id, tweet_mode='extended')
                Cleaner.clean_thread(thread)
                title = thread.title
                author_name = thread.user.name
                author_screen_name = thread.user.screen_name
                author_photo = thread.user.profile_image_url_https.replace(
                    "_normal.jpg", ".jpg").replace("_normal.png", ".png")
                author_describtion = thread.user.description

                try:
                    thumnail_photo_url = thread.entities['media'][0][
                        'media_url_https']
                    thumnail_photo = f'<img src="{thumnail_photo_url}" height="300" width="400">'
                except Exception:
                    thumnail_photo = '<img src="/static/img/default-thum.jpg" height="300" width="400">'

                if thread.lang == "ar":
                    rtl = True
                else:
                    rtl = False

                thread_tweets_ids = Grabber.grab_thread_tweets_ids(id)
                if len(thread_tweets_ids) > 0:
                    content = [
                        '<div class="tw-block">'+thread.full_text+'</div>']
                    for tweet_id in thread_tweets_ids:
                        tweet = cls.tweepy_client.get_status(
                            tweet_id, tweet_mode='extended')
                        if tweet.user.id != thread.user.id:
                            break
                        Cleaner.clean_tweet(tweet)
                        content.append(
                            '<div class="tw-block">' + tweet.full_text +
                            '</div>')
                    content = ''.join(content)

                    post = Post.objects.create(
                        id=id, content=content, author_name=author_name,
                        author_screen_name=author_screen_name,
                        author_photo=author_photo,
                        author_describtion=author_describtion, title=title,
                        thumnail_photo=thumnail_photo, rtl=rtl)
                    logger.info(
                        f"Collected {len(thread_tweets_ids) + 1} replies from thread id:{id} ")
                    cls.__add_post_to_user(
                        post=post, user_id=status.user.id_str)

                    cls.__reply_to_status(status=status)
                    cls.__send_notification(post)

        except Exception as e:
            logger.exception(f"Error handling {status.id}")

    @staticmethod
    def __send_notification(post):
        channel_layer = get_channel_layer()
        async_to_sync(
            channel_layer.group_send)(
            "notifier",
            {"type": "send.notification", "id": str(post.id),
             "thumnail_photo": post.thumnail_photo, "title": post.title,
             "created_at": post.created_at.strftime('%b %d, %Y'),
             "author_screen_name": post.author_screen_name,
             "rtl": post.rtl})

    @classmethod
    def __add_post_to_user(cls, post, user_id):
        collector_user = UserSocialAuth.objects.filter(
            uid=user_id).values('user_id').first()
        if collector_user:
            post.username.add(collector_user['user_id'])

    @classmethod
    def __reply_to_status(cls, status, old=False):
        if settings.APP_ENV == "dev":
            if old:
                reply = f''' @{status.user.screen_name} 🧵 already saved locally 🧵'''
            else:
                reply = f''' @{status.user.screen_name} 🧵 saved locally 🧵'''
        else:
            path = reverse('post', args=(status.in_reply_to_status_id,))
            r = requests.get(
                f'https://tinyurl.com/api-create.php?source=create&url={settings.APP_URL}{path}')
            reply = f''' @{status.user.screen_name} 🧵 {r.text} 🧵 '''

        cls.tweepy_client.update_status(
            status=reply, in_reply_to_status_id=status.id)
