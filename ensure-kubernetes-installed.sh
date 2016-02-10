#!/bin/bash

set -e

# Clone repo
(cd ~ && git clone https://github.com/GoogleCloudPlatform/kubernetes.git)

# Build go source
(cd ~/kubernetes && hack/build-go.sh)
