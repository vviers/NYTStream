import json
import requests
from kafka import SimpleProducer, KafkaClient, KafkaConsumer
import pyspark
import random

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
        
    # build query
    url = f'http://api.nytimes.com/svc/semantic/v2/concept/name/{types[concept_type]}/{concept}.json?fields=all&api-key={key}'
    
    # query the API, return JSON (as a python dict)
    result_dic = requests.get(url)
    if result_dic.status_code != 200:
        print("Something went wrong...")
        
    if len(result_dic.json()['results']) == 0:
        return []
    
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


if __name__ == "__main__":
    
    # consume Tweets with Kafka
    
    # extract
    tags = getTags(tweet)
    yago_tags = extractYago(tags)
    
    # make wikipedia link
    
    # cross with Yago
    topic = random.choice(yago_tags)
    
    # get table of relationships
    # Yago_Facts.tsv is chached, filter on `topic`
    # pick a random relationship
    # express it as a string
    
    # produce tweet to Kafka
    