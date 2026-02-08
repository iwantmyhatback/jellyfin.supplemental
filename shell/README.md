# jellyfin.supplemental/shell

The shell scripting portion of this script set. Handles environment sourcing, execution, and deployment (Docker).

### buildImage.sh

Rebuilds the Docker image and pulls down the Python dependency image.

### main.sh

The primary execution script. Can be run locally without Docker.

1. Sources environment variables from `<repoRoot>/configuration/environment.properties`
2. Creates and activates a Python virtual environment if needed
3. Installs pip dependencies from `<repoRoot>/requirements.txt` (includes `openapi-generator-cli[jdk4py]`)
4. Extracts the Jellyfin server URL from `<repoRoot>/configuration/info*.json`
5. Generates the Jellyfin API client from the server's OpenAPI spec (if not already present), applies patches, and installs it into the venv
6. Exports `DEVICE` and `DEVICE_ID` environment variables
7. Executes `<repoRoot>/python/main.py`

### runRoutine.sh

Docker deployment entry point. Pulls repository changes, rebuilds the Docker image if needed (on git changes, missing image, or `FORCE_DOCKER_REBUILD=TRUE`), then runs a disposable container executing `<repoRoot>/shell/main.sh`.

### sourceEnvironment.sh

Sources any variables defined in `<repoRoot>/configuration/environment.properties`.
