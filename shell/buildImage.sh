#! /usr/bin/env sh

# Delete existing Docker image and rebuild the image with current files
# Can be used when testing adhoc, but is also used by shell/runRoutine.sh in deployments

if [ -z "${ALREADY_SOURCED:-}" ]; then
  . sourceEnvironment.sh
else
  echo "[ENV] Skipping additional sourcing because ALREADY_SOURCED is defined"
fi

docker pull python
docker image rm jellyfin-supplemental
docker build --build-arg PYENV_LOCATION --build-arg DIRNAME="$(pwd)" -t jellyfin-supplemental ../