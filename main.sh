#! /usr/bin/env bash

# Perform the entire Check and Email routine
# Includes:
#   Ensuring script execution is within the repository
#   Export the environment variables set in environment.properties
#   Perform Pre-Python dependency checks and installed
#   Then execute the Python routine

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "${SCRIPT_DIR}" || exit


if [ -z "${ALREADY_SOURCED:-}" ]; then
  . sourceEnvironment.sh
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

python3 main.py