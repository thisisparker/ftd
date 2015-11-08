#!/usr/bin/env python3
# Tweets from the FOIA The Dead script.
# Tweets a subset of new requests, and blog post updates with digests.

import yaml
from twython import Twython

config = yaml.load(open("config.yaml"))

twitter_account = config['twitter_account']
twitter_app_key = config['twitter_app_key']
twitter_app_secret = config['twitter_app_secret']
twitter_oauth_token = config['twitter_oauth_token']
twitter_oauth_token_secret = config['twitter_oauth_token_secret']

twitter = Twython(twitter_app_key, twitter_app_secret, twitter_oauth_token, twitter_oauth_token_secret)

def tweet_request(name,obit_url):
    twitter.update_status(status='Just filed a FOIA request for the FBI file of {name}. NY Times obituary: {obit_url}'.format(**locals()))

def tweet_digest_post(post_title,post_url)
    twitter.update_status(status='Blog post: {post_title} {post_url}'.format(**locals()))
