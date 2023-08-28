from jellyfin_apiclient_python import JellyfinClient
from json import load as loadJson, dump as dumpJson
from os import environ as osEnviron, path as osPath

# Check whether we want to use secondary JSON file (mostly used for testing on a secondary machine)
REMOTE_CONNECTION = str(osEnviron.get("REMOTE_CONNECTION")).upper()

# Load the JSON file
if REMOTE_CONNECTION in ["YES", "TRUE"]:
    print(
        f"[ENV] REMOTE_CONNECTION={REMOTE_CONNECTION} passed in environment ..........")
    infoFile = open("../configuration/info.remote.json")
else:
    infoFile = open("../configuration/info.json")

info = loadJson(infoFile)


def jellyfinConnection():
    JELLYFIN = info.get("JELLYFIN")
    SERVER_URL = JELLYFIN.get("SERVER_URL")
    PORT = JELLYFIN.get("PORT")
    USERNAME = JELLYFIN.get("USERNAME")
    PASSWORD = JELLYFIN.get("PASSWORD")
    CREDENTIAL_LOCATION = JELLYFIN.get("CREDENTIAL_LOCATION")
    CLIENT_SECRET_FILE = JELLYFIN.get("CLIENT_SECRET_FILE")
    CREDENTIAL_FILE = f"{CREDENTIAL_LOCATION}/{CLIENT_SECRET_FILE}"

    client = JellyfinClient()
    client.config.app('jellyfin.supplemental', '0.0.1',
                      'administratorsMachine', 'adminMach')
    client.config.data["auth.ssl"] = True

    if not osPath.isfile(CREDENTIAL_FILE):
        client.auth.connect_to_address(f"{SERVER_URL}:{PORT}")
        client.auth.login(f"{SERVER_URL}:{PORT}", USERNAME, PASSWORD)
        credentials = client.auth.credentials.get_credentials()
        server = credentials["Servers"][0]
        server["username"] = USERNAME
        with open(CREDENTIAL_FILE, 'w', encoding='utf-8') as file:
            dumpJson(server, file, ensure_ascii=False, indent=4)

    credentialFile = open(CREDENTIAL_FILE)
    credentials = loadJson(credentialFile)
    client.authenticate({"Servers": [credentials]}, discover=False)
    return client
