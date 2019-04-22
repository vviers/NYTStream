#!/bin/python

from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
from time import sleep
import sys

# Read my (secret) credentials
with open(".twittercredentials") as creds:
    consumer_key, consumer_secret, access_token, access_token_secret = creds.read().split("\n")[0:4]
    
# Authenticate to the Twitter API
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

try:
    api = tweepy.API(auth)
except:
    print("Could not connect to Twitter API.")
    exit()
    
# read data from Kafka
KAFKA_TOPIC = sys.argv[1]
def consumeTweet():
    

def tweet(data):
    first_tweet = api.update_status(data["first_tweet"])
    second_tweet = api.update_status(data["second_tweet"], in_reply_to_status_id = first_tweet.id)
    print("Just Twitted.")
    
if __name__ == "__main__":
    while True:
        
