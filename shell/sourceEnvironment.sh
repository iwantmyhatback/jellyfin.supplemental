#! /usr/bin/env sh

# Export the environment variables set in configuration/environment.properties

echo "[ENV] Introducting configuration/environment.properties variables:"
while read -r variable; do
  if [ "${variable%"${variable#?}"}" = "#" ] || [ "${variable}" = '' ]; then
    continue
  else
    echo "[ENV] ${variable?}"
    export "${variable?}"
  fi
done < ../configuration/environment.properties
