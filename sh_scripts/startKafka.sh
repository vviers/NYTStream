#!/bin/bash

topicname=$1

sudo /usr/lib/kafka/bin/zookeeper-server-start.sh config/zookeeper.properties

sudo /usr/lib/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic $topicname
