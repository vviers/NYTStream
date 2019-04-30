#!/bin/python

from kafka import KafkaProducer, KafkaClient
import requests
from time import sleep
import json

# Read API key
with open("../.credentials", "r") as f:
    key = f.read().strip("\n")
    
# create a set to keep track of already seen articles
seen = set()

# Kafka settings
topic_out = 'raw_articles'
# Kafka producer
producer = KafkaProducer(bootstrap_servers="localhost:9092" , request_timeout_ms = 3000000, retries = 20)

if __name__=='__main__':

    while True:
        
        # Limit to articles published in the last 24 hours, query limit is 20 anyways...
        url = f'https://api.nytimes.com/svc/news/v3/content/all/all/24.json?api-key={key}'

        r = requests.get(url)

        while r.status_code != 200:
            print(f"Something wrong happened... Error code: {r.status_code}. Retrying in 60sec...")
            sleep(60)
            r = requests.get(url)

        data = r.json()

        for article in data["results"]:
            if article['title'] not in seen:

                print(f"Found a new article:\n\t {article['title']}")

                seen.add(article['title'])
                
                producer.send(topic_out, json.dumps(article).encode("utf-8"))
                      
        sleep(240)
