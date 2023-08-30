# jellyfin.supplemental/configuration

### environment.properties

environment variables to be sourced for the shell scripts (Booleans accept "TRUE|FALSE")
These variables are mostly used to make development testing easier on me

- PYENV_LOCATION : sets the location for the python3 venv
- TEST_MODE : removes all the BCC emails so the emails only come to me
- REMOTE_CONNECTION : forces my secondary config file (info.remote.json) for using a VPN connection
- FORCE_DOCKER_REBUILD : forces shell/runRoutine.sh to run shell/buildImage.sh regardless of commit changes
- ALREADY_SOURCED : used to check the environment for previous sourcing to prevent rendundant sourcing

### info.json / info.remote.json (Example dummy data in: info.sample.json)

Configuration information for the resources used to create and send the email content

- EMAIL
  - TO_LIST : The email destination (generally my email)
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
- TMDB
  - API_KEY : Valid API key for TMDB (used for Poster images)
