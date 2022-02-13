import os
import re
import time
import uuid
from mimetypes import guess_extension

import boto3
import requests
import tweepy
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer
from django.conf import settings
from social_django.models import UserSocialAuth

from posts.models import Post

auth = tweepy.OAuthHandler(
    settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
auth.set_access_token(settings.TWITTER_ACCESS_TOKEN,
                      settings.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
s3 = boto3.client('s3', aws_access_key_id=settings.S3_ACCESS_KEY,
                  aws_secret_access_key=settings.S3_SECRET_KEY)


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            if 'collect' in status.text.lower().split(" "):
                post_exsist = Post.objects.filter(
                    id=status.in_reply_to_status_id).first()
                if post_exsist:
                    try:
                        collector_user = UserSocialAuth.objects.filter(
                            uid=status.user.id_str).first()
                        if collector_user:
                            Post.objects.filter(id=status.in_reply_to_status_id).first(
                            ).username.add(collector_user.user.id)
                        r = requests.get(
                            f'https://tinyurl.com/api-create.php?source=create&url=https://thecollect0rapp.com/post/{post_exsist.id}')
                        api.update_status(
                            f'@{status.user.screen_name} Your 🧵 post is ready {r.text}', status.id)
                    except Exception:
                        pass
                else:
                    # thread's creator information #
                    screen_name = status.in_reply_to_screen_name
                    name = status.entities['user_mentions'][0]['name']
                    thread_id = status.in_reply_to_status_id
                    main = api.get_status(thread_id, tweet_mode='extended')
                    photo = main.user.profile_image_url_https.replace(
                        "_normal.jpg", ".jpg").replace("_normal.png", ".png")
                    description = self.clean_string(main.user.description)
                    # thumnail photo #
                    try:
                        thum_url = main.entities['media'][0]['media_url_https']
                        s3_thum_url = self.upload2s3(thread_id, thum_url)
                        thum = f''' <img src="{s3_thum_url}" height="300" width="400" > '''
                    except Exception:
                        thum = ''' <img src="/static/img/default-thum.jpg" height="300" width="400"> '''

                    # getting all thread tweets #
                    thread_tweets = []
                    req = requests.get(
                        "https://mobile.twitter.com/{0}/status/{1}".format(screen_name, thread_id))
                    bs4 = BeautifulSoup(req.content, "html.parser")
                    for el in bs4.findAll('table', class_="tweet", href=True):
                        if "{0}/status/".format(screen_name) in el.attrs["href"]:
                            thread_tweets.append(
                                el.attrs["href"].split("/")[3].split('?')[0])
                        else:
                            break

                    # getting content #
                    final_content = []
                    if len(thread_tweets) > 0:
                        thread_tweets.insert(0, thread_id)
                        for index, tweet in enumerate(thread_tweets):
                            tweet_details = api.get_status(
                                tweet, tweet_mode='extended')
                            text = tweet_details.full_text
                            # getting title #
                            if index == 0:
                                title = self.clean_string(text)
                            content = self.clean_urls(tweet_details, text)
                            content = self.clean_media(
                                thread_id, tweet_details, content)
                            content = self.clean_string(content)
                            final_content.append(content+'<br><br>')
                        final_content = ''.join(final_content)
                        final_content = "<p class='article__text'>" + final_content + '</p>'

                        Post(id=thread_id, content=final_content, author_name=name,
                             author_screen_name=screen_name, author_photo=photo, author_describtion=description, title=title, thumnail_photo=thum).save()

                        collector_user = UserSocialAuth.objects.filter(
                            uid=status.user.id_str).first()
                        if collector_user:
                            Post.objects.filter(id=status.in_reply_to_status_id).first(
                            ).username.add(collector_user.user.id)
                        try:
                            channel_layer = get_channel_layer()
                            sync_to_async(channel_layer.group_send)('posts', {'type': 'send.notification', "post_id": str(
                                thread_id), 'thumnail_photo': thum, 'title': title, })
                            r = requests.get(
                                f'https://tinyurl.com/api-create.php?source=create&url=https://thecollect0rapp.com/post/{thread_id}')
                            api.update_status(
                                f'@{status.user.screen_name} Your 🧵 post is ready {r.text}', status.id)
                        except Exception as e:
                            print(e)
            else:
                pass
        except Exception as e:
            print(e)
            pass

    def on_error(self, status_code):
        if status_code == 420:
            time.sleep(60)
            return True

    def clean_string(self, string):
        twitter_urls = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
        for url in twitter_urls:
            if "t.co" in url:
                string = string.replace(url, "")
        return string

    def clean_media(self, thread_id, tweet_details, text):
        res = text
        try:
            for i in range(len(tweet_details.extended_entities['media'])):
                if "ext_tw_video" in tweet_details.extended_entities['media'][i]['media_url_https']:
                    for j in range(len(tweet_details.extended_entities['media'][i]['video_info']['variants'])):
                        if ".mp4" in tweet_details.extended_entities['media'][i]['video_info']['variants'][j]['url']:
                            mp4_url = tweet_details.extended_entities[
                                'media'][i]['video_info']['variants'][j]['url']
                            s3_mp4 = self.upload2s3(thread_id, mp4_url)
                            res += f''' <br><br><video width="400" controls> <source src="{s3_mp4}" type="video/mp4"> </video><br><br> '''
                            break
                elif tweet_details.extended_entities['media'][i]['type'] == "animated_gif":
                    for j in range(len(tweet_details.extended_entities['media'][i]['video_info']['variants'])):
                        if ".mp4" in tweet_details.extended_entities['media'][i]['video_info']['variants'][j]['url']:
                            mp4_url = tweet_details.extended_entities[
                                'media'][i]['video_info']['variants'][j]['url']
                            s3_mp4 = self.upload2s3(thread_id, mp4_url)
                            res += f''' <br><video autoplay loop muted inline><source src="{s3_mp4}" type="video/mp4"></video><br> '''
                            break
                else:
                    img_url = tweet_details.extended_entities['media'][i]['media_url_https']
                    s3_img = self.upload2s3(thread_id, img_url)
                    res += f''' <br><a href="{s3_img}" class="article__gallery">
									<img src="{s3_img}" alt=""></a><br> '''
            return res
        except Exception as e:
            print(e)
            return res

    def clean_urls(self, tweet_details, text):
        res = list(text)
        try:
            for i in range(len(tweet_details.entities['urls'])-1, -1, -1):
                url = tweet_details.entities["urls"][i]["expanded_url"]
                indice = tweet_details.entities["urls"][i]["indices"][0]
                display_url = tweet_details.entities["urls"][i]["display_url"]
                if "status" and "twitter.com" in url:
                    res.insert(
                        indice, f''' <br><br></p><blockquote class="twitter-tweet"><a href="{url}"></a></blockquote><p class='article__text'><br><br> ''')
                elif 'youtu.be' in url or 'youtube' in url:
                    if 'watch' in url:
                        res.insert(
                            indice, f''' <br><br><iframe width="500" height="300" src="{url.replace('watch?v=','embed/')}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe><br><br> ''')
                    elif 'channel' in url or 'user' in url:
                        res.insert(
                            indice, f''' <br><br><a target="_blank" href="{url}">{display_url}</a><br><br> ''')
                    else:
                        res.insert(
                            indice, f''' <br><br><iframe width="500" height="300" src="https://www.youtube.com/embed/{url.split('/')[-1]}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe><br><br> ''')
                else:
                    res.insert(
                        indice, f''' <br><br><a target="_blank" href="{url}">{display_url}</a><br><br> ''')
            return ''.join(res)
        except Exception:
            return ''.join(res)

    def upload2s3(self, thread_id, url):
        name = str(thread_id) + str(uuid.uuid4().hex[:8])
        while True:
            try:
                with requests.get(url, allow_redirects=True, stream=True) as r:
                    name = name + \
                        str(guess_extension(r.headers['content-type']))
                    with open(name, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                    s3.upload_file(name, 'collect0r', name, ExtraArgs={
                                   'ContentType': r.headers['content-type']})
                if os.path.isfile(name):
                    os.remove(name)
                print("Upload Successful")
                break
            except Exception as e:
                time.sleep(1)
                print(e)
        return f'https://collect0r.s3.us-east-2.amazonaws.com/{name}'


def start_stream(stream, **kwargs):
    try:
        print("started")
        stream.filter(**kwargs)
    except Exception as e:
        print(e)
        start_stream(stream, **kwargs)


myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
start_stream(myStream, track=['@thecollect0rapp'], stall_warnings=True)
