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
    echo "[INFO] [ENV] Skipping additional sourcing because ALREADY_SOURCED is defined"
fi

if [ -d "${PYENV_LOCATION}" ]; then
    echo "[INFO] [PY_ENV] ${PYENV_LOCATION} does exist."
else
    echo "[INFO] [PY_ENV] ${PYENV_LOCATION} does not exist"
    python3 -m venv "${PYENV_LOCATION}"
fi

. "${PYENV_LOCATION}/bin/activate"

# Determine which info file to use (mirrors logic in python/jellyfin.py)
if [ "${REMOTE_CONNECTION:-}" = "TRUE" ] || [ "${REMOTE_CONNECTION:-}" = "YES" ]; then
    INFO_FILE="${REPO_ROOT_DIR}/configuration/info.remote.json"
else
    INFO_FILE="${REPO_ROOT_DIR}/configuration/info.json"
fi

JELLYFIN_URL=$(python3 -c "
import json
info = json.load(open('${INFO_FILE}'))
j = info['JELLYFIN']
print(f\"{j['SERVER_URL']}:{j['PORT']}\")
")

JELLYFIN_CLIENT_DIR="${PYENV_LOCATION}/jellyfin-client"

if [ ! -d "${JELLYFIN_CLIENT_DIR}" ] || [ "${FORCE_CLIENT_REGEN:-}" = 'TRUE' ]; then
    echo "[INFO] [OPENAPI] Generating Jellyfin API client from ${JELLYFIN_URL}/api-docs/openapi.json"
    openapi-generator generate \
        -i "${JELLYFIN_URL}/api-docs/openapi.json" \
        -g python \
        -o "${JELLYFIN_CLIENT_DIR}" \
        --package-name jellyfin_api \
        --skip-validate-spec

    # Patch: pydantic validate_call strips enums to str, but serializer calls .value
    sed -i.bak 's/type\.value/type.value if hasattr(type, '\''value'\'') else type/g' \
        "${JELLYFIN_CLIENT_DIR}/jellyfin_api/api/remote_image_api.py"
    rm -f "${JELLYFIN_CLIENT_DIR}/jellyfin_api/api/remote_image_api.py.bak"

    pip install "${JELLYFIN_CLIENT_DIR}"
else
    echo "[INFO] [OPENAPI] Jellyfin API client already exists at ${JELLYFIN_CLIENT_DIR}"
fi

export HOSTNAME="$(hostname)"

pip install --requirement requirements.txt
# pip freeze > requirements.txt

python3 -Bu python/main.py