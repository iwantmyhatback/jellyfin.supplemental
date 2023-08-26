import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import json

TEST_MODE = str(os.environ.get("TEST_MODE")).upper()

infoFile = open("info.json")
info = json.load(infoFile)

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
    home_dir = os.path.expanduser("~")
    credential_dir = os.path.join(os.getcwd(), CREDENTIAL_LOCATION)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(
        credential_dir, "gmail-python-email-send.json")
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print("Storing credentials to " + credential_path)
    else:
        credString = open(".credentials/gmail-python-email-send.json").read()
        credentials = client.OAuth2Credentials.from_json(credString)
        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)
        store.put(credentials)
    return credentials


def SendMessage(sender, to, bcc, subject, msgHtml, msgPlain):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    credentials.refresh(http)
    service = discovery.build("gmail", "v1", http=http)
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
    except errors.HttpError as error:
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
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}


def main(plainMessage, htmlMessage):
    to = TO_LIST
    sender = SENDER_STRING
    bcc = BCC_LIST
    subject = SUBJECT_STRING
    SendMessage(sender, to, bcc, subject, htmlMessage, plainMessage)


if __name__ == "__main__":
    main()
