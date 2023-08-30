# jellyfin.supplemental

This is a small script set which leverages a few external resources to gather media information and send an email which describes the Movies and Shows which have been updated in the Jellyfin instance within the past 7 days. There are a couple prerequisites to running this script:<br>

- An existing [Jellyfin](https://jellyfin.org) setup holding personal media collection
- A [Google Cloud Account](https://console.cloud.google.com/) for leveraging the Gmail API to send an email

Though designed to run through a Docker container using the entry script `<repoRoot>/shell/runRoutine.sh` it can also be run locally without a Docker container using `<repoRoot>/shell/main.sh`.

The scripting is POSIX compliant (usable with most modern shells), and the python code uses Python3 (tested with 3.11.4)

**To get things running user will need to:**

1. Have a configured Jellyin instance with valid user credentials
2. Create a Google account and Provide a secret file (see [Credentials Readme](.credentials/README.md))
3. Provide all the required information for the configuration files (see [Configuration Readme](configuration/README.md))
4. Authorize the Gmail consent screen from console on first run
5. Set a `cron` task (or some other scheduling) to run weekly

For additional information see README's for:<br>
[credentials](.credentials/README.md)<br>
[configuration](configuration/README.md)<br>
[python](python/README.md)<br>
[shell](shell/README.md)<br>
