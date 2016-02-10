#!/bin/bash

set -e

docker build -t eu.gcr.io/$GCLOUD_PROJECT/$DOCKER_IMAGE_NAME:$CIRCLE_SHA1 .
docker tag -f eu.gcr.io/$GCLOUD_PROJECT/$DOCKER_IMAGE_NAME:$CIRCLE_SHA1 eu.gcr.io/$GCLOUD_PROJECT/$DOCKER_IMAGE_NAME:latest
gcloud docker push eu.gcr.io/$GCLOUD_PROJECT/$DOCKER_IMAGE_NAME:$CIRCLE_SHA1
gcloud docker push eu.gcr.io/$GCLOUD_PROJECT/$DOCKER_IMAGE_NAME:latest
