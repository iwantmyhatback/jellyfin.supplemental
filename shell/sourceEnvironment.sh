#! /usr/bin/env sh

# Export the environment variables set in configuration/environment.properties

REPO_ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT_DIR}" || exit

echo "[ENV] Introducting configuration/environment.properties variables:"
while read -r variable; do
  if [ "${variable%"${variable#?}"}" = "#" ] || [ "${variable}" = '' ]; then
    continue
  else
    echo "[ENV] ${variable?}"
    export "${variable?}"
  fi
done < "${REPO_ROOT_DIR}/configuration/environment.properties"
