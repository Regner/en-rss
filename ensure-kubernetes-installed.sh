#!/bin/bash

set -e

if [[ -d ~/kubernetes ]]; then
  cd ~/kubernetes && git pull
else
  cd ~ && git clone https://github.com/GoogleCloudPlatform/kubernetes.git
fi

# Build go source
cd ~/kubernetes && hack/build-go.sh
