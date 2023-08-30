# jellyfin.supplemental/.credentials

Storage location for credential tokens and secret files. I have included some sample files for the purpose of debugging issues with configuration, though **the only file that the user should need to put into place is the `<repoRoot>/.credentials/gmail-secret-file.json`**

### gmail-secret-file.json

**This file is placed here by the user** after being generated in the Google Cloud Console. It is used by oAuth to authenticate with the Gmail sending account

To get this file you need to:

- **Create an Account**
  - Create a new Google account to be your email sending account (I dont recommend using your personal email for this) which I will now refer to as <sendingEmailAddress>
- **Project Setup**
  - Navigate to the [Google Cloud Console](https://console.cloud.google.com/) and login with <sendingEmailAddress>
    - Create a Project take note of the project name you use. I will now refer to this name as <projectName>
    - Navigate to the "API Library" and enable the [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com) for your new project
- **Credential**
  - Navigate to [oAuth Consent Screen Setup](https://console.cloud.google.com/apis/credentials/consent) and configure it
    - **oAuth Consent Screen**
      - Select "Configure Consent Screen"
      - Select External
      - Enter "App Name" (<projectName>)
      - Enter "User Support Email" (<sendingEmailAddress>)
      - Enter "Developer Contact Information" (<sendingEmailAddress>)
    - **Scopes**
      - Select "Add or Remove Scopes"
      - In "Manually Add Scopes" text box enter "https://www.googleapis.com/auth/gmail.send" (You may be able to find and select it instead of entering manually)
      - Verfiy that your scope is selected and select "Update"
    - **Test Users**
      - Select "+ Add Users"
      - Add <sendingEmailAddress> and select "Add"
      - Select "Save and Continue"
      - Review your Summary and Select "Back To Dashboard"
  - Navigate to [API & Services > Credentials](https://console.cloud.google.com/apis/credentials)
    - Select "+ Create Credentials" > "oAuth Client ID"
    - Select "Application Type" as "Desktop App"
    - Enter "Name" (<projectName>)
    - Once complete download the JSON file
- Rename your JSON file and stage in `<repoRoot>/.credentials/gmail-secret-file.json`
- _Note:_ that the first time this secret file is used, the console will send you to a Google page (or provide you a link) to authorize on your consent screen

### gmail-secret-file.sample.json

A sample of what a correct `<repoRoot>/.credentials/gmail-secret-file.json` should look like. This is simply for validation of newly generated files to make sure they match this template. Seeing as Gmail offers a few different ways of authenticating between service accounts, oAuth, and API keys i am providing this to make sure that the correct file is queried by the user in the Google Cloud Console

### gmail-python-email-send.json

**This file is generated** by the `<repoRoot>/python/gmail.py` execution using the Gmail provided secrets file `<repoRoot>/.credentials/gmail-secret-file.json` and configuration information in `<repoRoot>/configuration/info*.json`.

### gmail-python-email-send.sample.json

A sample of what a correct `<repoRoot>/.credentials/gmail-python-email-send.json` should look like. This is simply for validation of newly generated files to make sure they match this template. The `<repoRoot>/python/gmail.py` execution should generate something just like this with no user intervention if the configuration file (`<repoRoot>/configuration/info*.json`) and secret file (`<repoRoot>/.credentials/gmail-secret-file.json`) are correctly set up

### jellyfin-credentials.json

**This file is generated** by the `<repoRoot>/python/connection.py` execution using the Jellyfin credentials and server information provided in the configuration file `<repoRoot>/configuration/info*.json`

### jellyfin-credentials.sample.json

A sample of what a correct `<repoRoot>/.credentials/jellyfin-credentials.json` should look like. This is simply for validation of newly generated files to make sure they match this template. The `<repoRoot>/python/connection.py` execution should generate something just like this with no user intervention if the configuration file (`<repoRoot>/configuration/info*.json`) is correctly set up
