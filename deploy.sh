#!/bin/bash

set -e

gcloud config set container/cluster $CLUSTER_NAME
gcloud container clusters get-credentials $CLUSTER_NAME

echo $CIRCLE_SHA1

envsubst < $RC_FILE > tmp-rc.yml
./kubernetes/cluster/kubectl.sh rolling-update $RC_NAME -f tmp-rc.yml