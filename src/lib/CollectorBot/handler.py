

import tweepy
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
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
                collector_user = UserSocialAuth.objects.filter(
                    uid=status.user.id_str).first()
                if collector_user:
                    post.username.add(collector_user.user_id)
                url = f'{settings.APP_URL}/post/{post.id}'
                # r = requests.get(
                #     f'https://tinyurl.com/api-create.php?source=create&url={url}')
                # api.update_status(
                #     f'@{status.user.screen_name} Your 🧵 post is ready {r.text}',
                #     status.id)

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

                thread_tweets_ids = Grabber.grab_thread_tweets_ids(id)
                if len(thread_tweets_ids) > 0:
                    content = [thread.full_text+'<br><br>']
                    for tweet_id in thread_tweets_ids:
                        tweet = cls.tweepy_client.get_status(
                            tweet_id, tweet_mode='extended')
                        if tweet.user.id != thread.user.id:
                            break
                        Cleaner.clean_tweet(tweet)
                        content.append(tweet.full_text+'<br><br>')
                    content = ''.join(content)
                    content = "<p class='article__text'>" + content + '<br><br> </p>'

                    post = Post.objects.create(
                        id=id, content=content, author_name=author_name,
                        author_screen_name=author_screen_name,
                        author_photo=author_photo,
                        author_describtion=author_describtion, title=title,
                        thumnail_photo=thumnail_photo)
                    logger.info(
                        f"collected {len(thread_tweets_ids) + 1} replies from thread id:{id} ")
                    collector_user = UserSocialAuth.objects.filter(
                        uid=status.user.id_str).values('user_id').first()
                    if collector_user:
                        post.username.add(collector_user['user_id'])
                    # r = requests.get(
                    #     f'https://tinyurl.com/api-create.php?source=create&url=https://thecollect0rapp.com/post/{thread_id}')
                    reply = f''' @{status.user.screen_name} 🧵 saved locally '''
                    cls.tweepy_client.update_status(
                        status=reply, in_reply_to_status_id=status.id)

                    cls.send_notification(post)

        except Exception as e:
            logger.exception(f"error handling {status.id}")

    @staticmethod
    def send_notification(post):
        channel_layer = get_channel_layer()
        async_to_sync(
            channel_layer.group_send)(
            "notifier",
            {"type": "send.notification", "id": str(post.id),
             "thumnail_photo": post.thumnail_photo, "title": post.title})
