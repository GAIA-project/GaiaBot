#!/usr/bin/env bash
./build.sh
docker build -t gaiabot:1.1 .
docker tag gaiabot:1.1 qopbot/gaiabot:1.1
docker push qopbot/gaiabot:1.1
