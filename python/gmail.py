from httplib2 import Http
from os import environ as osEnviron, path as osPath, makedirs as osMakedirs, getcwd as osGetCwd
from json import load as loadJson
from base64 import urlsafe_b64encode
from oauth2client import client as oa2Client, tools as oa2Tools, file as oa2File
from apiclient import errors as apiErrors, discovery as apiDiscovery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase

TEST_MODE = str(osEnviron.get("TEST_MODE")).upper()

infoFile = open("configuration/info.json")
info = loadJson(infoFile)

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

# Dont email everyone if youre testing
if TEST_MODE in ["YES", "TRUE"]:
    BCC_LIST = []


# Retrieve the credentials using google CLIENT_SECRET_FILE
def get_credentials():
    home_dir = osPath.expanduser("~")
    credential_dir = osPath.join(osGetCwd(), CREDENTIAL_LOCATION)
    if not osPath.exists(credential_dir):
        osMakedirs(credential_dir)
    credential_path = osPath.join(
        credential_dir, "gmail-python-email-send.json")
    store = oa2File.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = oa2Client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = oa2Tools.run_flow(flow, store)
        print("Storing credentials to " + credential_path)
    else:
        credString = open(
            f"{CREDENTIAL_LOCATION}/gmail-python-email-send.json").read()
        credentials = oa2Client.OAuth2Credentials.from_json(credString)
        http = credentials.authorize(Http())
        credentials.refresh(http)
        store.put(credentials)
    return credentials


def SendMessage(sender, to, bcc, subject, msgHtml, msgPlain):
    credentials = get_credentials()
    http = credentials.authorize(Http())
    credentials.refresh(http)
    service = apiDiscovery.build("gmail", "v1", http=http)
    message1 = CreateMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result


def SendMessageInternal(service, user_id, message):
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        print(f"[INFO] Gmail Message Sent ... ID : {message['id']}")
        return message
    except apiErrors.HttpError as error:
        print(f"[ERROR] An error occurred: {error}")
        return "Error"
    return "OK"


def CreateMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain):
    message = MIMEMultipart("alternative")
    message["To"] = ", ".join(to)
    message["Bcc"] = ", ".join(bcc)
    message["From"] = sender
    message["Subject"] = subject

    message.attach(MIMEText(msgPlain, "plain"))
    message.attach(MIMEText(msgHtml, "html"))
    return {"raw": urlsafe_b64encode(message.as_bytes()).decode()}


def main(plainMessage, htmlMessage):
    to = TO_LIST
    sender = SENDER_STRING
    bcc = BCC_LIST
    subject = SUBJECT_STRING
    SendMessage(sender, to, bcc, subject, htmlMessage, plainMessage)


if __name__ == "__main__":
    main()
