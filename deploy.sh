#!/bin/bash

set -e

gcloud config set container/cluster $1
gcloud container clusters get-credentials $1

envsubst < $2 > tmp-rc.yml
./kubernetes/cluster/kubectl.sh rolling-update $3 -f tmp-rc.yml