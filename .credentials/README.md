# jellyfin.supplemental/.credentials

Storage location for credential tokens and secret files. I have included some sample files for the purpose of debugging issues with configuration, though _the only file that the user should need to put into place is the `<repoRoot>/.credentials/gmail-secret-file.json`_

### gmail-python-email-send.json

_This file is generated_ by the `<repoRoot>/python/gmail.py` execution using the Gmail provided secrets file `<repoRoot>/.credentials/gmail-secret-file.json` and configuration information in `<repoRoot>/configuration/info*.json`.

### gmail-python-email-send.sample.json

A sample of what a correct `<repoRoot>/.credentials/gmail-python-email-send.json` should look like. This is simply for validation of newly generated files to make sure they match this template. The `<repoRoot>/python/gmail.py` execution should generate something just like this with no user intervention if the configuration file (`<repoRoot>/configuration/info*.json`) and secret file (`<repoRoot>/.credentials/gmail-secret-file.json`) are correctly set up

### gmail-secret-file.json

_This file is placed here by the user_ after being generated in the Google Developer Console. It is used by oAuth to authenticate with the Gmail sending account

### gmail-secret-file.sample.json

A sample of what a correct `<repoRoot>/.credentials/gmail-secret-file.json` should look like. This is simply for validation of newly generated files to make sure they match this template. Seeing as Gmail offers a few different ways of authenticating between service accounts, oAuth, and API keys i am providing this to make sure that the correct file is queried by the user in the Google developer console

### jellyfin-credentials.json

_This file is generated_ by the `<repoRoot>/python/connection.py` execution using the Jellyfin credentials and server information provided in the configuration file `<repoRoot>/configuration/info*.json`

### jellyfin-credentials.sample.json

A sample of what a correct `<repoRoot>/.credentials/jellyfin-credentials.json` should look like. This is simply for validation of newly generated files to make sure they match this template. The `<repoRoot>/python/connection.py` execution should generate something just like this with no user intervention if the configuration file (`<repoRoot>/configuration/info*.json`) is correctly set up
