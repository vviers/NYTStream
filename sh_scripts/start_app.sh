#!/bin/bash

nohup python nytscraper.py &
sleep 5
nohup python translator.py &
python tweets_enhancer.py &
python twitteur.py &