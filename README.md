# jellyfin.supplemental

This is a small script set that leverages an existing Jellyfin setup and a Gmail developer account (Gmail API) to gather and send an email which describes the Movies and Shows which have been updated in the past 7 days. Though I have designed this to run through Docker with the entry script `<repoRoot>/shell/runRoutine.sh` it can also be run locally without a Docker container using `<repoRoot>/shell/main.sh`.

The scripting should is POSIX compliant, and the python code uses python3 (tested with 3.11.4)

See information on:<br>
[configuration](configuration/README.md)<br>
[python](python/README.md)<br>
[shell](shell/README.md)<br>
