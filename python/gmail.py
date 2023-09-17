from httplib2 import Http
from os import environ as osEnviron, path as osPath, makedirs as osMakedirs, getcwd as osGetCwd
from json import load as loadJson, dumps as dumpsJson
from base64 import urlsafe_b64encode
from oauth2client import client as oa2Client, tools as oa2Tools, file as oa2File
from apiclient import errors as apiErrors, discovery as apiDiscovery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging as log

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


def main(plainMessage, htmlMessage):
    log.debug(f'[FUNCTION] gmail/main({plainMessage}, {htmlMessage})')
    to = TO_LIST
    sender = SENDER_STRING
    bcc = BCC_LIST
    subject = SUBJECT_STRING
    SendMessage(sender, to, bcc, subject, htmlMessage, plainMessage)
    log.debug(f'[RETURN] gmail/main : 0')
    return 0


def get_credentials():
    log.debug('[FUNCTION] gmail/get_credentials()')
    home_dir = osPath.expanduser("~")
    credential_dir = osPath.join(osGetCwd(), CREDENTIAL_LOCATION)
    if not osPath.exists(credential_dir):
        osMakedirs(credential_dir)

    credential_path = osPath.join(
        credential_dir, "gmail-python-email-send.json")
    store = oa2File.Storage(credential_path)
    credentials = store.get()
    if not credentials:
        flow = oa2Client.flow_from_clientsecrets(
            f"{credential_dir}/{CLIENT_SECRET_FILE}", SCOPES)
        flow.user_agent = APPLICATION_NAME
        args = oa2Tools.argparser.parse_args()
        args.noauth_local_webserver = True
        credentials = oa2Tools.run_flow(flow, store, args)
        print("Storing credentials to " + credential_path)

    else:
        credentials = store.get()
        http = credentials.authorize(Http())
        credentials.refresh(http)
        store.put(credentials)

    log.debug(f'[RETURN] gmail/get_credentials : {credentials}')
    return credentials


def SendMessage(sender, to, bcc, subject, msgHtml, msgPlain):
    log.debug(
        f'[FUNCTION] gmail/SendMessage( {sender}, {to}, {bcc}, {subject}, {msgHtml}, {msgPlain} )')
    credentials = get_credentials()
    http = credentials.authorize(Http())
    service = apiDiscovery.build("gmail", "v1", http=http)
    message1 = CreateMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    log.debug(f'[RETURN] gmail/SendMessage : {result}')
    return result


def SendMessageInternal(service, user_id, message):
    log.debug(
        f'[FUNCTION] gmail/SendMessageInternal( {service}, {user_id}, {message} )')
    try:
        message = service.users().messages().send(
            userId=user_id, body=message).execute()
        print(f"[INFO] Gmail Message Sent .......... ID : {message['id']}")
        log.debug(f'[RETURN] gmail/SendMessageInternal : {message}')
        return message

    except apiErrors.HttpError as error:
        print(f"[ERROR] An error occurred: {error}")
        log.warning(f'[RETURN] gmail/SendMessageInternal : Error')
        return "Error"

    log.debug(f'[RETURN] gmail/SendMessageInternal : OK')
    return "OK"


def CreateMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain):
    log.debug(
        f'[FUNCTION] gmail/CreateMessageHtml( {sender}, {to}, {bcc}, {subject}, {msgHtml}, {msgPlain} )')
    message = MIMEMultipart("alternative")
    message["To"] = ", ".join(to)
    message["Bcc"] = ", ".join(bcc)
    message["From"] = sender
    message["Subject"] = subject

    message.attach(MIMEText(msgPlain, "plain"))
    message.attach(MIMEText(msgHtml, "html"))
    result = {"raw": urlsafe_b64encode(message.as_bytes()).decode()}
    log.debug(f'[RETURN] gmail/CreateMessageHtml : {result}')
    return result
