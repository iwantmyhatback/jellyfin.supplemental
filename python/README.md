# jellyfin.supplemental/python

The Python content for this script set. Contains the data querying and processing as well as the Gmail API utilization for email sending

### connection.py

Uses configuration files from `<repoRoot>/configuration/info*.json` to connect to Jellyfin and return a client to `<repoRoot>/python/jellyfin.py`

### gmail.py

Uses configuration files from `<repoRoot>/configuration/info*.json` to connect to Gmail and use the API to send an Email (in `<repoRoot>/shell/main.sh`)

### htmlProcessing.py

Processes the compiled information in the `main` function of `<repoRoot>/python/jellyfin.py` into HTML and returns it to `<repoRoot>/python/gmail.py` for the email body

### jellyfin.py

Queries information from Jellyfin and processes the data to prepare it for HTML generation by `<repoRoot>/python/htmlProcessing.py`

### main.py

Performs all the actions laid out in the other Python files (Runs all the python code from `<repoRoot>/shell/main.sh`)

### utilities.py

Small random functions besing used to perform tasks that dont fit into the context of other Python files
