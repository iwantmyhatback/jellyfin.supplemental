#! /usr/bin/env sh

# Export the environment variables set in environment.properties
# Perform Pre-Python dependency checks and installed
# Then execute the Python routine

echo "[ENV] Introducting environment.properties variables:"
while read -r variable; do
  echo "[ENV] ${variable?}"
  export "${variable?}"
done < environment.properties

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