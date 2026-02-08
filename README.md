# jellyfin.supplemental

This is a small script set which leverages the Gmail API to send an email describing the Movies and Series updated on a provided Jellyfin instance within the past N days (user defined). There are a couple prerequisites to running this script:<br>

- (Required) An existing [Jellyfin](https://jellyfin.org) setup containing a personal media collection
- (Required) A [Google Cloud Account](https://console.cloud.google.com/) for leveraging the Gmail API to send an email
- (Required) Python 3.10+ with pip
- (Optional) A Docker installation on the machine running the script

Though designed to run through a Docker container using the entry script `<repoRoot>/shell/runRoutine.sh`, it can also be run locally without a Docker container using `<repoRoot>/shell/main.sh`.

The shell scripting is POSIX compliant (usable with most modern shells), and the Python code uses Python 3 (tested with 3.14).

The Jellyfin API client is auto-generated from the server's OpenAPI spec using `openapi-generator-cli` (installed via pip with a bundled JDK — no system Java or Homebrew required). The generated client lives in the Python venv and is gitignored.

**To get things running user will need to:**

1. Have a configured Jellyfin instance with valid user credentials
2. Create a Google account and provide `<repoRoot>/.credentials` with a secret file (see [Credentials README](.credentials/README.md))
3. Provide all required information for the configuration files `<repoRoot>/configuration/info*.json` (see [Configuration README](configuration/README.md))
4. Authorize the Gmail API oAuth consent screen from console on first run
5. Set a `cron` task (or some other scheduling) to every Nth day

For additional information see README's for:<br>
[Credentials README](.credentials/README.md)<br>
[Configuration README](configuration/README.md)<br>
[Python README](python/README.md)<br>
[Shell README](shell/README.md)<br>
