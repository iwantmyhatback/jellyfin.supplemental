#!/usr/bin/env sh

# Perform the entire Check and Email routine and all the Deployment tasks
# Includes:
#   Ensuring script execution is within the repository
#   Getting repository changes
#   Rebuilding Docker image if there were any git changes
#   Run the shell/main.sh script in a disposable docker container

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd )
cd "${SCRIPT_DIR}" || exit

. sourceEnvironment.sh

PREVIOUS_COMMIT=$(git rev-list HEAD -n 1)
git pull

if [ "${PREVIOUS_COMMIT}" != "$(git rev-list HEAD -n 1)" ] || [ "${FORCE_DOCKER_REBUILD:-}" = 'TRUE' ]; then
    if [ "${FORCE_DOCKER_REBUILD:-}" = 'TRUE' ]; then
        echo "[INFO] FORCE_DOCKER_REBUILD is active... Rebuilding image"
    else
        echo "[INFO] Found changes to jellyfin-supplemental... Rebuilding image"
    fi
    "${SCRIPT_DIR}/buildImage.sh"
else
    echo "[INFO] No changes to jellyfin-supplemental"
fi

docker run --env-file "../configuration/environment.properties" --rm --name jellyfin-supplemental jellyfin-supplemental:latest shell/main.sh