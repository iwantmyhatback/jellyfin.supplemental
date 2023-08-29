# jellyfin.supplemental/shell

The shell scripting portion of this script set. Mostly handling environment, execution, and deployment (docker)

## buildImage.sh

Rebuilds the docker image and pulls down the python dependency image

## main.sh

Generates and activates the pythion virtual environment if needed and performs the python execution of `<repoRoot>/python/main.py`
This would be the script for execution if you want to run the scripts locally without using Docker

## runRoutine.sh

Checks for any changes to the repository after a pull, if there are changes then `<repoRoot>/shell/buildImage.sh` regenerates the docker images using the new source code. Proceeds to run a disposable container which executes `<repoRoot>/shell/main.sh`

## sourceEnvironment.sh

Sources any variables defined in `<repoRoot>/configuration/environment.properties`
