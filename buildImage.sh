#! /usr/bin/env sh

# Delete existing Docker image and rebuild the image with current files
# Can be used when testing adhoc, but is also used by runRoutine.sh in deployments

docker pull python
docker image rm jellyfin-supplemental
docker build -t jellyfin-supplemental .