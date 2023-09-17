#! /usr/bin/env sh

# Delete existing Docker image and rebuild the image with current files
# Can be used when testing adhoc, but is also used by shell/runRoutine.sh in deployments

REPO_ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT_DIR}" || exit

if [ -z "${ALREADY_SOURCED:-}" ]; then
    . "${REPO_ROOT_DIR}/shell/sourceEnvironment.sh"
else
    echo "[INFO] [ENV] Skipping additional sourcing because ALREADY_SOURCED is defined"
fi

echo "[INFO] [DOCKER] Start Docker Python image update (Pull)"
docker pull python
echo "[INFO] [DOCKER] Remove old jellyfin-supplemental image"
docker image rm jellyfin-supplemental
echo "[INFO] [DOCKER] Build new jellyfin-supplemental image"
docker build --build-arg PYENV_LOCATION --build-arg DIRNAME="${REPO_ROOT_DIR}" -t jellyfin-supplemental ./