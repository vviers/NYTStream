#!/bin/python

from googletrans import Translator
import json
from kafka import KafkaProducer, KafkaClient, KafkaConsumer
from time import sleep

if __name__=="__main__":

        # kafka settings
        topic_in = "raw_articles"
        topic_out = "translated"

        producer = KafkaProducer(bootstrap_servers = 'localhost:9092', retries = 2000)

        consumer = KafkaConsumer(topic_in,
                        #auto_offset_reset='earliest', # for dev only
                        value_deserializer=lambda m: json.loads(m.decode('utf-8')))

        print("Kafka started for translator.")

        # create Translator instance
        translator = Translator()

        for msg in consumer:
                # read tweet
                tweet = msg.value

                # translate title
                translation = translator.translate(tweet['title'], src="en", dest="fr")
                title_translated = translation.text

                # translate abstract
                translation = translator.translate(tweet['abstract'], src="en", dest="fr")
                abstract_translated = translation.text

                # append data 
                tweet["translations"] = {"title":title_translated, "abstract":abstract_translated}
                to_send = tweet

                print(tweet["translations"])

                # produce tweet to Kafka
                producer.send(topic_out, json.dumps(to_send).encode("utf-8"))

