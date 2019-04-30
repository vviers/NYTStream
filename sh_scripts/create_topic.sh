#!/bin/bash
topicname=$1
/usr/lib/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 2 --partitions 1 --topic $topicname
