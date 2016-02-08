#!/bin/bash

cat > ens-rss-rc.yml <<EOF
apiVersion: v1
kind: ReplicationController
metadata:
  name: en-rss-dev
  labels:
    name: en-rss-dev
    version: v1
spec:
  replicas: 1
  selector:
    name: en-rss-dev
    version: v1
  template:
    metadata:
      labels:
        name: en-rss-dev
        version: v1
    spec:
      containers:
        - name: en-rss-dev
          image: eu.gcr.io/eve-notifications/en-rss:latest
          resources:
            limits:
              cpu: 50m
EOF