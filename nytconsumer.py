#!/bin/python

#!/usr/bin/env python
from kafka import KafkaConsumer

# Kafka settings
topic = 'twitter-stream'

if __name__ == '__main__':
    print("consumer started")
    consumer = KafkaConsumer(topic)

    for msg in consumer:
        print(msg)