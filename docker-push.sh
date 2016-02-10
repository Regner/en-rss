#!/bin/bash

set -e

docker build -t $DOCKER_IMAGE_NAME:$CIRCLE_SHA1 .
docker tag -f $DOCKER_IMAGE_NAME:$CIRCLE_SHA1 $DOCKER_IMAGE_NAME:latest
gcloud docker push $DOCKER_IMAGE_NAME:$CIRCLE_SHA1
gcloud docker push $DOCKER_IMAGE_NAME:latest
