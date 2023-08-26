#!/usr/bin/env bash

# Perform the entire Check and Email routine and all the Deployment tasks
# Includes:
#   Getting repository changes
#   Rebuilding Docker image if there were any git changes
#   Run the main.sh script in a disposable docker container

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "${SCRIPT_DIR}" || exit

PREVIOUS_COMMIT=$(git rev-list HEAD -n 1)
git pull

if [ "${PREVIOUS_COMMIT}" != "$(git rev-list HEAD -n 1)" ]; then
    echo "Found changes to jellyfin-supplemental... Rebuilding image"
    "${SCRIPT_DIR}/buildImage.sh"
else
    echo "No changes to jellyfin-supplemental"
fi

docker run --rm --name jellyfin-supplemental jellyfin-supplemental:latest ./main.sh