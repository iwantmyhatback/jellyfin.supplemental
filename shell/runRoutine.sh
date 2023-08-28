#!/usr/bin/env sh

# Perform the entire Check and Email routine and all the Deployment tasks
# Includes:
#   Ensuring script execution is within the repository
#   Getting repository changes
#   Rebuilding Docker image if there were any git changes
#   Run the shell/main.sh script in a disposable docker container

REPO_ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT_DIR}" || exit

. "${REPO_ROOT_DIR}/shell/sourceEnvironment.sh"

echo "[GIT] Start git repository update (Pull)"
PREVIOUS_COMMIT=$(git rev-list HEAD -n 1)
git pull

if [ "${PREVIOUS_COMMIT}" != "$(git rev-list HEAD -n 1)" ] || [ "${FORCE_DOCKER_REBUILD:-}" = 'TRUE' ]; then
    if [ "${FORCE_DOCKER_REBUILD:-}" = 'TRUE' ]; then
        echo "[INFO] FORCE_DOCKER_REBUILD is active... Rebuilding image"
    else
        echo "[INFO] Found changes to jellyfin-supplemental... Rebuilding image"
    fi
    "${REPO_ROOT_DIR}/shell/buildImage.sh"
else
    echo "[INFO] No changes to jellyfin-supplemental"
fi

docker run --env-file "${REPO_ROOT_DIR}/configuration/environment.properties" --rm --name jellyfin-supplemental jellyfin-supplemental:latest ${REPO_ROOT_DIR}/shell/main.sh