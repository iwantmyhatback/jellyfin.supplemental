#! /usr/bin/env sh

# Perform the entire Check and Email routine
# Includes:
#   Ensuring script execution is within the repository
#   Export the environment variables set in configuration/environment.properties
#   Perform Pre-Python dependency checks and installed
#   Then execute the Python routine

REPO_ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT_DIR}" || exit


if [ -z "${ALREADY_SOURCED:-}" ]; then
  . "${REPO_ROOT_DIR}/shell/sourceEnvironment.sh"
else
  echo "[ENV] Skipping additional sourcing because ALREADY_SOURCED is defined"
fi

if [ -d "${PYENV_LOCATION}" ]; then
  echo "[INFO] ${PYENV_LOCATION} does exist."
else
  echo "[INFO] ${PYENV_LOCATION} does not exist"
  python3 -m venv "${PYENV_LOCATION}"
fi

. "${PYENV_LOCATION}/bin/activate"

pip install --quiet --requirement requirements.txt
# pip freeze > requirements.txt

python3 -Bu python/main.py