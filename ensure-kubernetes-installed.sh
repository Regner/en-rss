#!/bin/bash

set -e

if [[ -d ~/kubernetes ]]; then
  rm -rf ~/kubernetes
fi

function get_latest_version_number {
  local -r latest_url="https://storage.googleapis.com/kubernetes-release/release/stable.txt"
  curl -Ss ${latest_url}
}

release=$(get_latest_version_number)
release_url=https://storage.googleapis.com/kubernetes-release/release/${release}/kubernetes.tar.gz
file=kubernetes.tar.gz

echo "Downloading kubernetes release ${release} to ${PWD}/kubernetes.tar.gz"
curl -L -o ${file} ${release_url}

echo "Unpacking kubernetes release ${release}"
tar -xzf ${file}
rm ${file}
