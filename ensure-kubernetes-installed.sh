#!/bin/bash

set -e


if [[ -d ~/kubernetes ]]; then
  echo "Kubernetes already installed"
  rm -rf ~/kubernetes
else
  echo "Installing Kubernetes..."
fi


curl -sS https://get.k8s.io | bash
