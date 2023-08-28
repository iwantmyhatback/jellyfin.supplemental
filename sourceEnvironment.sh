#! /usr/bin/env sh

# Export the environment variables set in environment.properties

echo "[ENV] Introducting environment.properties variables:"
while read -r variable; do
  if [ "${variable%"${variable#?}"}" = "#" ] || [ "${variable}" = '' ]; then
    continue
  else
    echo "[ENV] ${variable?}"
    export "${variable?}"
  fi
done < environment.properties
