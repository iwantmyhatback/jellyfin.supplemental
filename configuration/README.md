# jellyfin.supplemental/configuration

### environment.properties

environment variables to be sourced for the shell scripts (Booleans accept "TRUE|FALSE")
These variables are mostly used to make development testing easier on me

- PYENV_LOCATION : Sets the location path for the python3 venv \[ PATH \]
- PYTHON_LOG_LEVEL : Sets the log level string for python logging module \[ DEBUG | INFO | WARNING | ERROR | CRITICAL \]
- TEST_MODE : Sets a boolean trigger to remove all the BCC emails (so the notification emails only come to admin) \[ TRUE | FALSE \]
- REMOTE_CONNECTION : Sets a boolean trigger to force the secondary config file (info.remote.json) for using a VPN connection \[ TRUE | FALSE \]
- FORCE_DOCKER_REBUILD : Sets a boolean trigger to force shell/runRoutine.sh to run shell/buildImage.sh regardless of commit changes \[ TRUE | FALSE \]
- DAY_THRESHOLD : Sets an integer representing the inclusion threshold (the maximum valid number of days since adding a media item) \[ INTEGER \]

### info.json / info.remote.json (Example dummy data in: info.sample.json)

Configuration information for the resources used to create and send the email content

- EMAIL
  - TO_LIST : The email destination (generally admin email)
  - SENDER_STRING : The email doing the sending (which has oAuth setup for the gmail API)
  - BCC_LIST : Any other email address which should receive the email (empty array for none)
  - SUBJECT_STRING : Email subject line string
- GMAIL
  - CLIENT_SECRET_FILE : Name of the secret file from Gmail (default:"gmail-secret-file.json")
  - CREDENTIAL_LOCATION : Location for Gmail generated/provided credentials (default: ".credentials")
  - SCOPES : oAuth scopes for credentials (default: "https://www.googleapis.com/auth/gmail.send")
  - APPLICATION_NAME : Your application name which was used in Gmail API configuration
- JELLYFIN
  - SERVER_URL : Jellyfin URL or IP address
  - PORT : Jellyfin Port number
  - API_KEY : Jellyfin API Key
  - USERNAME : Jellyfin User Name
  - PASSWORD : Jellyfin User Password
  - CREDENTIAL_LOCATION : Location for Jellyfin generated/provided credentials (default: ".credentials")
  - CLIENT_SECRET_FILE : Name of the secret file from Jellyfin (default:"jellyfin-credentials.json")
