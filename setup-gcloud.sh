#!/bin/bash

set -e

echo $CLIENT_SECRET | base64 --decode > ${HOME}/client-secret.json
gcloud auth activate-service-account --key-file ${HOME}/client-secret.json
gcloud config set project $GCLOUD_PROJECT
gcloud config set compute/zone $GCLOUD_ZONE
gcloud docker --authorize-only