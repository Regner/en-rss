#!/bin/bash

set -e

gcloud config set container/cluster $1
gcloud container clusters get-credentials $1

envsubst < $2 > tmp-rc.yml
./kubernetes/cluster/kubectl.sh delete rc $3
./kubernetes/cluster/kubectl.sh create -f tmp-rc.yml