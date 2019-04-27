#!/bin/python

#!/usr/bin/env python
from kafka import KafkaConsumer

# Kafka settings
topic = 'raw_articles'

if __name__ == '__main__':
    print("consumer started")
    consumer = KafkaConsumer(topic, auto_offset_reset='earliest')

    for msg in consumer:
        print(msg)
