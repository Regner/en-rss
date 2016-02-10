#!/bin/bash

set -e

if [[ -d ~/kubernetes ]]; then
  rm -rf ~/kubernetes
fi

# Clone repo
(cd ~ && git clone https://github.com/GoogleCloudPlatform/kubernetes.git)

# Build go source
(cd ~/kubernetes && hack/build-go.sh)
