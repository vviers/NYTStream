#!/bin/bash

gcloud dataproc clusters create nyt-cluster \
 --subnet default --zone europe-west2-a --master-machine-type n1-standard-2 --master-boot-disk-size 500 --num-masters 1 --worker-machine-type n1-standard-2 --worker-boot-disk-size 500 --image-version 1.3-deb9 --project st446-vviers --bucket 'nyt-project' \
 --initialization-actions 'gs://dataproc-initialization-actions/jupyter/jupyter.sh','gs://dataproc-initialization-actions/python/pip-install.sh','gs://dataproc-initialization-actions/zookeeper/zookeeper.sh','gs://dataproc-initialization-actions/kafka/kafka.sh' \
 --metadata 'PIP_PACKAGES=sklearn pandas graphframes pyspark==2.3.2 kafka-python tweepy oauth2client googletrans', --metadata 'run-on-master=true'
