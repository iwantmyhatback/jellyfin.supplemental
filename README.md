# jellyfin.supplemental

This is a small script set that leverages an existing Jellyfin setup and a Gmail developer account (Gmail API) to gather and send an email which describes the Movies and Shows which have been updates in the past 7 days. Though I have designed this to run through Docker with the entry script `shell/runRoutine.sh` it can also be run without a Docker container using `shell/main.sh`.

The scripting should all be POSIX compliant, and the python code uses python3 (tested with 3.11.4)
