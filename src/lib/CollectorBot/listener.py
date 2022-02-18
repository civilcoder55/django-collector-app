import time

import tweepy
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from posts.models import Post
from social_django.models import UserSocialAuth

from .cleaner import Cleaner
from .grabber import Grabber


class StreamListener(tweepy.Stream):

    def __init__(self):
        super().__init__(**settings.TWITTER_SECRETS)
        auth = tweepy.OAuthHandler(**settings.TWITTER_SECRETS)
        self.tweepy_client = tweepy.API(auth)

    def on_status(self, status):
        try:
            if 'collect' in status.text.lower().split(" "):
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
                    thread = self.tweepy_client.get_status(
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
                            tweet = self.tweepy_client.get_status(
                                tweet_id, tweet_mode='extended')
                            if tweet.user.id != thread.user.id:
                                break
                            Cleaner.clean_tweet(tweet)
                            content.append(tweet.full_text+'<br><br>')
                        content = ''.join(content)
                        content = "<p class='article__text'>" + content + '<br><br> </p>'

                        post = Post(
                            id=id, content=content, author_name=author_name,
                            author_screen_name=author_screen_name,
                            author_photo=author_photo,
                            author_describtion=author_describtion, title=title,
                            thumnail_photo=thumnail_photo).save()
                        print(f"post {id} collected")
                        collector_user = UserSocialAuth.objects.filter(
                            uid=status.user.id_str).first()
                        if collector_user:
                            post.username.add(collector_user.user_id)
                        try:
                            # r = requests.get(
                            #     f'https://tinyurl.com/api-create.php?source=create&url=https://thecollect0rapp.com/post/{thread_id}')
                            reply = f''' @{status.user.screen_name} 🧵 saved locally '''
                            self.tweepy_client.update_status(
                                status=reply, in_reply_to_status_id=status.id)

                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)
                            (
                                'notifier',
                                {
                                    'type': 'send.notification',
                                    "id": id,
                                    'thumnail_photo': thumnail_photo,
                                    'title': title
                                }
                            )

                        except Exception as e:
                            print(e)

        except Exception as e:
            print(e)

    def on_error(self, status_code):
        if status_code == 420:
            time.sleep(60)
            return True
