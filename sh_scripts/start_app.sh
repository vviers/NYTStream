#!/bin/bash

nohup python ../src/nytscraper.py &
sleep 5
nohup python ../src/translator.py &
nohup python ../src/tweets_enhancer.py &
nohup python ../src/twitteur.py &
echo "Twitter Bot Started :)"
