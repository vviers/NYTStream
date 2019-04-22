#!/bin/python

from kafka import SimpleProducer, KafkaClient
import requests
from time import sleep
import json

# Read API key
with open(".credentials", "r") as f:
    key = f.read().strip("\n")
    
# create a set to keep track of already seen articles
seen = set()

# Kafka settings
topic = 'NYTARTICLES'
# Kafka producer
kafka = KafkaClient('localhost:9092')
producer = SimpleProducer(kafka)

while True:
    
    # Limit to articles published in the last 24 hours, query limit is 20 anyways...
    url = f'https://api.nytimes.com/svc/news/v3/content/all/all/24.json?api-key={key}'

    r = requests.get(url)

    while r.status_code != 200:
        print(f"Something wrong happened... Error code: {r.status_code}. Retrying...")
        sleep(10)

    data = r.json()

    for article in data["results"]:
        if article['title'] not in seen:

            print(f"Found a new article:\n\t {article['title']}")

            seen.add(article['title'])
                  
            with open("some_data_json.txt", "a") as outfile:
                outfile.write(json.dumps(article) + "\n")
            
            producer.send_messages(topic, json.dumps(article).encode("utf-8"))
                  
    sleep(240)
