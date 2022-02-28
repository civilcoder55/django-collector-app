
import re

from fastcore.transform import Pipeline


class Cleaner:

    @staticmethod
    def __clean_urls(tweet):
        try:
            text = list(tweet.full_text)
            for url in reversed(tweet.entities['urls']):
                expanded_url = url["expanded_url"]
                index = url["indices"][0]
                display_url = url["display_url"]
                if "status" in expanded_url and "twitter.com" in expanded_url:
                    text.insert(
                        index,
                        f''' <br><br></p><blockquote class="twitter-tweet"><a href="{expanded_url}"></a></blockquote><p class="article__text"><br><br> ''')
                elif 'youtu.be' in expanded_url or 'youtube' in expanded_url:
                    if 'watch' in expanded_url:
                        text.insert(
                            index,
                            f''' <br><br><iframe width="500" height="300" src="{expanded_url.replace('watch?v=','embed/')}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe><br><br> ''')
                    elif 'channel' in expanded_url or 'user' in expanded_url:
                        text.insert(
                            index,
                            f''' <br><br><a target="_blank" dir href="{expanded_url}">{display_url}</a><br><br> ''')
                    else:
                        text.insert(
                            index,
                            f'''<br><br><iframe width="500" height="300" src="https://www.youtube.com/embed/{expanded_url.split('/')[-1]}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe><br><br>''')
                else:
                    text.insert(
                        index,
                        f''' <br><br><a target="_blank" dir href="{expanded_url}">{display_url}</a><br><br> ''')
            tweet.full_text = ''.join(text)

        except:
            pass

        finally:
            return tweet

    @staticmethod
    def __clean_media(tweet):
        try:
            for media in tweet.extended_entities['media']:
                if media['type'] == 'video':
                    mp4_url = sorted(
                        media['video_info']['variants'],
                        key=lambda v: v.get('bitrate', 0),
                        reverse=True)[0]['url']
                    tweet.full_text += f''' <br><br><video width="400" controls> <source src="{mp4_url}" type="video/mp4"></video><br><br> '''

                elif media['type'] == "animated_gif":
                    mp4_url = media['video_info']['variants'][0]['url']
                    tweet.full_text += f''' <br><video autoplay loop muted inline><source src="{mp4_url}" type="video/mp4"></video><br> '''

                else:
                    img_url = media['media_url_https']
                    tweet.full_text += f''' <br><a href="{img_url}" class="article__gallery"><img src="{img_url}"></a><br> '''

        except:
            pass

        finally:
            return tweet

    @staticmethod
    def __clean_text(tweet):
        try:
            tweet.full_text = re.sub(
                r'https:\/\/t\.co\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                "", tweet.full_text)

        except:
            pass

        finally:
            return tweet

    @staticmethod
    def __clean_user_description(tweet):
        try:
            for url in tweet.user.entities['description']['urls']:
                tweet.user.description = tweet.user.description.replace(
                    url['url'], url['expanded_url'])
        except:
            pass

        finally:
            return tweet

    @staticmethod
    def set_title(tweet):
        tweet.title = tweet.full_text
        return tweet

    @classmethod
    def clean_tweet(cls, tweet):
        """Function to clean,prettify and wrap tweet_text with html,
        Args:
            tweet (Status): tweepy tweet status object

        Returns:
            Status: cleaned version of tweet object
        """
        pipe = Pipeline(
            [cls.__clean_urls, cls.__clean_media, cls.__clean_text])
        return pipe(tweet)

    @classmethod
    def clean_thread(cls, tweet):
        """Function to clean,prettify and wrap thread_tweet_text with html,
        Args:
            tweet (Status): tweepy tweet status object

        Returns:
            Status: cleaned version of tweet object
        """
        pipe = Pipeline(
            [cls.__clean_text, cls.set_title, cls.__clean_urls, cls.__clean_media,
             cls.__clean_text, cls.__clean_user_description])
        return pipe(tweet)
