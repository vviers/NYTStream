#!/bin/python

import json
import requests
from kafka import KafkaProducer, KafkaClient, KafkaConsumer
from pyspark import SparkContext
from pyspark.sql import *
import random
from time import sleep

# NYT Credentials
with open(".credentials", "r") as f:
    key = f.read().strip("\n")


def getTags(tweet):
    '''retrieve all tags about organisations, people, and places for a given article'''
    
    def tags(tag):   
        '''lists the NYT tags'''     
        if isinstance(tag, str):
            return []
        elif isinstance(tag, list):
            return [h for h in tag]

    all_tags = {"org":tags(tweet['org_facet']), "per":tags(tweet['per_facet']), "geo":tags(tweet['geo_facet'])}
    
    return all_tags

    
def getSemantic(concept, concept_type, key = key):
    '''query the NewYorkTimes semantic API'''
    
    types = {'des':'nytd_des', 'geo':'nytd_geo', 'org':'nytd_org', 'per':'nytd_per'}
    
    if concept_type not in types:
        raise ValueError(f"concept_type must be one of {types}")
        
    if len(concept) == 0:
        return []
        
    # build Semantic API query
    url = f'http://api.nytimes.com/svc/semantic/v2/concept/name/{types[concept_type]}/{concept}.json?fields=all&api-key={key}'
    
    # query the API, return JSON (as a python dict)
    result_dic = requests.get(url)
    # if didn't succeed, retry once
    if result_dic.status_code != 200:
        print(f"Something went wrong with the API call... Status Code: {result_dic.status_code}. Retrying once...")
        sleep(90)
        result_dic = requests.get(url)
        if result_dic.status_code != 200:
            print(f"Something went wrong with the API call... Status Code: {result_dic.status_code}.")
            return []

    # if empty, return empty
    if len(result_dic.json()['results']) == 0:
        return []
    
    # else return
    return result_dic.json()['results'][0]


def yagoExists(semantic):
    '''Check whether a given NYT semantic concept could be found in Yago database.
       This uses the fact that Yago concepts use their Wikipedia name.'''
    
    if "links" not in semantic:
        return False
    
    for link in semantic["links"]:
        if link["link_type"] == "wikipedia_raw_name":
            print("You may be able to find this concept on wikipedia:")
            print("https://en.wikipedia.org/wiki/" + link["link"])
            return link["link"]       
    return False


def extractYago(tags):
    '''Get the Yago/WikiData tags'''
    yagoconcepts = []
    for typ in tags:
        semantics = [getSemantic(t, typ) for t in tags[typ]]
        yagoconcepts += [yagoExists(s) for s in semantics]
    return [y for y in yagoconcepts if y]

def str_cleaner(s):
    '''Makes the Yago names more readable.'''
    return s.replace("<", "").replace(">", "").replace("_", " ")

def data_enhancer(subject):
    '''Query the Yago database for a random fact about a New York Times Article'''

    # subset the data to the subject
    subset = df.filter(f'subject == "{subject}"').collect()
    
    # make sure data is not empty, else return a wikipedia article
    if len(subset) == 0:
        return "More context here: https://en.wikipedia.org/wiki/" + "subject"
    
    # get a fact at random
    fact = random.choice(subset).asDict()
    
    # get URL of object
    url = "https://en.wikipedia.org/wiki/" + fact["object"].replace("<", "").replace(">", "")
    
    # generate the tweet
    tweet = str_cleaner(f'FACT: {fact["subject"]} {fact["predicate"]} {fact["object"]}') + f'\n {url}'
    
    return tweet


if __name__ == "__main__":
    
    # Start Spark
    sc = SparkContext(appName="NYT_Yago")
    spark = SparkSession.builder \
    .master("local") \
    .appName("NYT_Yago").getOrCreate()
    
    # Load Static Yago Data
    df = sc.textFile("file:///home/vincent/NYT_Stream/data/yagoFacts.tsv")
    df = df.map(lambda line: line.split("\t"))
    df = spark.createDataFrame(df, schema = ["ID", "subject", "predicate", "object", "value"])
    
    # produce and consume Tweets with Kafka
    
    topic_in = "translated"
    topic_out = "facts"
    
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    
    consumer = KafkaConsumer(topic_in,
            #auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    print("Kafka started.")
    
    for msg in consumer:
        # extract
        tweet = msg.value
        print(tweet["title"])
        tags = getTags(tweet)
        yago_tags = extractYago(tags)
        if len(yago_tags) == 0:
            fact = "No info found in the Yago data.\nhttps://www.mpi-inf.mpg.de/departments/databases-and-information-systems/research/yago-naga/yago/"
        else:
            tag = "<" + random.choice(yago_tags) + ">"
    
            fact = data_enhancer(tag)
        
        print("\n"+fact+"\n")
        
        tweet["fact"] = fact
        to_send = tweet

        # produce tweet to Kafka
        producer.send(topic_out, json.dumps(to_send).encode("utf-8"))
        # sleep so that the NYT API doesn't complain
        # sleep(60)
    
