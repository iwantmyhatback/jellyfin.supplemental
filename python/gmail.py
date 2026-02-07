from os import environ as osEnviron, path as osPath, makedirs as osMakedirs, getcwd as osGetCwd
from json import load as loadJson, dumps as dumpsJson
from base64 import urlsafe_b64encode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging as log

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient import errors as apiErrors


#################
## Definitions ##
#################

# Importing of required configuration values and environment settings
infoFile = open("configuration/info.json")
info = loadJson(infoFile)
log.debug(f'[LOAD] configuration/info.json : \n{dumpsJson(info, indent=2)}')

GMAIL = info.get("GMAIL")
SCOPES = GMAIL.get("SCOPES")
CLIENT_SECRET_FILE = GMAIL.get("CLIENT_SECRET_FILE")
CREDENTIAL_LOCATION = GMAIL.get("CREDENTIAL_LOCATION")
APPLICATION_NAME = GMAIL.get("APPLICATION_NAME")

EMAIL = info.get("EMAIL")
TO_LIST = EMAIL.get("TO_LIST")
SENDER_STRING = EMAIL.get("SENDER_STRING")
BCC_LIST = EMAIL.get("BCC_LIST")
SUBJECT_STRING = EMAIL.get("SUBJECT_STRING")

TEST_MODE = str(osEnviron.get("TEST_MODE")).upper()
if TEST_MODE in ["YES", "TRUE"]:
    log.info('[ENV] TEST_MODE is ACTIVE')
    BCC_LIST = []


# getCredentials() Performs the Gmail oAuth flow. Creates the credential location and file through authorization or refresh
def getCredentials():
    log.debug('[FUNCTION] gmail/getCredentials()')
    credential_dir = osPath.join(osGetCwd(), CREDENTIAL_LOCATION)
    if not osPath.exists(credential_dir):
        osMakedirs(credential_dir)

    credential_path = osPath.join(credential_dir, "gmail-python-email-send.json")
    client_secret_path = osPath.join(credential_dir, CLIENT_SECRET_FILE)
    creds = None

    # Load existing credentials from the stored token file
    if osPath.exists(credential_path):
        creds = Credentials.from_authorized_user_file(credential_path, [SCOPES])

    # If no valid credentials, either refresh or run the full auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log.info('[AUTH] Refreshing expired access token')
            creds.refresh(Request())
        else:
            log.info('[AUTH] Running full authorization flow')
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, [SCOPES])
            creds = flow.run_local_server(port=0)

        # Persist the credentials for future runs
        with open(credential_path, "w") as token_file:
            token_file.write(creds.to_json())
        log.info(f'[AUTH] Credentials stored to {credential_path}')

    log.debug(f'[RETURN] gmail/getCredentials : {creds}')
    return creds


# sendMessage() Authorizes, builds the API object, creates the message HTML, and sends the email
def sendMessage(sender, to, bcc, subject, msgHtml, msgPlain):
    log.debug(
        f'[FUNCTION] gmail/sendMessage({sender}, {to}, {bcc}, {subject}, {msgHtml}, {msgPlain})')
    credentials = getCredentials()
    service = build("gmail", "v1", credentials=credentials)
    message1 = createMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain)
    result = sendMessageInternal(service, "me", message1)
    log.debug(f'[RETURN] gmail/sendMessage : {result}')
    return result


# sendMessageInternal() Sends the email
def sendMessageInternal(service, user_id, message):
    log.debug(
        f'[FUNCTION] gmail/sendMessageInternal({service}, {user_id}, {message})')
    try:
        message = service.users().messages().send(
            userId=user_id, body=message).execute()
        print(f"[INFO] Gmail Message Sent .......... ID : {message['id']}")
        log.debug(f'[RETURN] gmail/sendMessageInternal : {message}')
        return message

    except apiErrors.HttpError as error:
        print(f"[ERROR] An error occurred: {error}")
        log.warning(f'[RETURN] gmail/sendMessageInternal : Error')
        return "Error"

    log.debug(f'[RETURN] gmail/sendMessageInternal : OK')
    return "OK"


# createMessageHtml() Uses the email info and created email data to construct the email object
def createMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain):
    log.debug(
        f'[FUNCTION] gmail/createMessageHtml({sender}, {to}, {bcc}, {subject}, {msgHtml}, {msgPlain})')
    message = MIMEMultipart("alternative")
    message["To"] = ", ".join(to)
    message["Bcc"] = ", ".join(bcc)
    message["From"] = sender
    message["Subject"] = subject

    message.attach(MIMEText(msgPlain, "plain"))
    message.attach(MIMEText(msgHtml, "html"))
    result = {"raw": urlsafe_b64encode(message.as_bytes()).decode()}
    log.debug(f'[RETURN] gmail/createMessageHtml : {result}')
    return result


################
## Executions ##
################

# main() Performs the functionality of this file. Sending an email with the generated html information
def main(plainMessage, htmlMessage):
    log.debug(f'[FUNCTION] gmail/main({plainMessage}, {htmlMessage})')
    to = TO_LIST
    sender = SENDER_STRING
    bcc = BCC_LIST
    subject = SUBJECT_STRING
    sendMessage(sender, to, bcc, subject, htmlMessage, plainMessage)
    log.debug(f'[RETURN] gmail/main : 0')
    return 0
