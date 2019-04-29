#!/bin/python
import json
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
from time import sleep
from kafka import KafkaConsumer
import random
import re

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
topic_in = "facts"

def tweet(data):
    
    def hashtag(hasht):
        '''makes a list of potential hashtags from the NYT tags'''                
        parentheses = re.compile(r"\((.+)\)")                        
        if isinstance(hasht, str):
            return []
        elif isinstance(hasht, list):
            return ["#" + re.sub(parentheses, "", h).lower().replace(" ", "").replace(',', '') for h in hasht]
    
    all_hashtags = hashtag(data['des_facet']) + hashtag(data['org_facet']) + hashtag(data['per_facet']) + hashtag(data['geo_facet'])
    
    first_twit = f'{data["translations"]["title"]}\n{data["url"]}'
    total_length = len(first_twit)
    # keep track of already used hashtag
    used_hashtags = set()

    # 20 tries in total
    if len(all_hashtags) > 0:
        n=0
        while total_length < 240 and n < 20:
            # pick candidate hashtag at random
            candidate_hashtag = random.choice(all_hashtags)
            # append it if still space
            if total_length + len(candidate_hashtag) < 240 and candidate_hashtag not in used_hashtags:
                first_twit += " " + candidate_hashtag # add ht
                total_length += len(candidate_hashtag) # update length tweet
                used_hashtags.add(candidate_hashtag) # update set of used ht

            n += 1

    try:
        first_tweet = api.update_status(first_twit)
        sleep(5)
        second_tweet = api.update_status(data["translations"]['abstract'], in_reply_to_status_id = first_tweet.id)
        sleep(7)
        third_tweet = api.update_status(data["fact"], in_reply_to_status_id = second_tweet.id)
        print(f"Just Twitted. {data['slug_name']}")
    except: print("Couldn't Tweet...")
    
if __name__ == "__main__":
    

    consumer = KafkaConsumer(topic_in, #auto_offset_reset='earliest',
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))


    for msg in consumer:
        # tweet, keep track of tweet id
        tw_id = tweet(msg.value)
        sleep(60)
