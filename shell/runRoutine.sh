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

echo "[INFO] [GIT] Start git repository update (Pull)"
PREVIOUS_COMMIT=$(git rev-list HEAD -n 1)
if git pull 2>&1; then
    GIT_PULL_OK=true
else
    echo "[WARN] [GIT] git pull failed (no upstream tracking or network issue). Continuing with local state."
    GIT_PULL_OK=false
fi

# Determine if Docker image needs to be built
IMAGE_EXISTS=$(docker image inspect jellyfin-supplemental:latest >/dev/null 2>&1 && echo true || echo false)

if [ "${FORCE_DOCKER_REBUILD:-}" = 'TRUE' ]; then
    echo "[INFO] [DOCKER] FORCE_DOCKER_REBUILD is active .......... Rebuilding image"
    "${REPO_ROOT_DIR}/shell/buildImage.sh"
elif [ "${IMAGE_EXISTS}" = 'false' ]; then
    echo "[INFO] [DOCKER] No existing image found .......... Building image"
    "${REPO_ROOT_DIR}/shell/buildImage.sh"
elif [ "${GIT_PULL_OK}" = 'true' ] && [ "${PREVIOUS_COMMIT}" != "$(git rev-list HEAD -n 1)" ]; then
    echo "[INFO] [DOCKER] Found changes to jellyfin-supplemental .......... Rebuilding image"
    "${REPO_ROOT_DIR}/shell/buildImage.sh"
else
    echo "[INFO] [DOCKER] No changes to jellyfin-supplemental"
fi

echo "[INFO] [DOCKER] Start the Docker run for jellyfin-supplemental:latest"
docker run --env-file "${REPO_ROOT_DIR}/configuration/environment.properties" --rm --name jellyfin-supplemental jellyfin-supplemental:latest ${REPO_ROOT_DIR}/shell/main.sh