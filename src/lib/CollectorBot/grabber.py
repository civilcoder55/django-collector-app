import json
import re
from urllib.parse import urlencode

import requests


class Grabber:
    token = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
    guest_token = None

    @classmethod
    def __get_guest_token(cls):
        """Function to get new guest token for twitter

        Returns:
            string: new guest token
        """
        res = requests.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers={'authorization': cls.token})
        if res.status_code == 200:
            return res.json()['guest_token']
        return None

    @classmethod
    def grab_thread_tweets_ids(cls, thread_id, cursor=None):
        """Function to grab all thread tweets

        Args:
            thread_id (string): id of thread to fetch 
            cursor (strign, optional): cursor value for next page. Defaults to None.

        Returns:
            list[string]: list of thread tweets ids
        """
        if not cls.guest_token:
            cls.guest_token = cls.__get_guest_token()

        variables = {
            "focalTweetId": str(thread_id),
            "with_rux_injections": "false",
            "includePromotedContent": "false",
            "withCommunity": "false",
            "withQuickPromoteEligibilityTweetFields": "false",
            "withBirdwatchNotes": "false",
            "withSuperFollowsUserFields": "false",
            "withDownvotePerspective": "false",
            "withReactionsMetadata": "false",
            "withReactionsPerspective": "false",
            "withSuperFollowsTweetFields": "false",
            "withVoice": "false",
            "withV2Timeline": "false",
            "__fs_dont_mention_me_view_api_enabled": "false",
            "__fs_interactive_text_enabled": "false",
            "__fs_responsive_web_uc_gql_enabled": "false"
        }

        if cursor:
            variables["cursor"] = cursor
            variables["referrer"] = "tweet"

        query = urlencode({'variables': json.dumps(variables)})
        url = f"https://mobile.twitter.com/i/api/graphql/P3-tzII5Lel_LoJH10ga-Q/TweetDetail?{query}"
        res = requests.get(
            url,
            headers={'authorization': cls.token,
                     'x-guest-token': cls.guest_token})

        if res.status_code == 403:
            cls.guest_token = None
            return cls.grab_thread_tweets_ids(
                thread_id=thread_id, cursor=cursor)

        matches = re.findall(
            r"conversationthread-(?:[0-9]*)-tweet-([0-9]*)", res.text)

        if len(matches) < 30:
            return matches

        has_more = re.search(
            r'"value":"(.*)","cursorType":"ShowMore"', res.text)

        if has_more:
            cursor = has_more.group(1)
            return matches + cls.grab_thread_tweets_ids(
                thread_id=thread_id, cursor=cursor)
        else:
            return matches
