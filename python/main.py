from gmail import main as sendGmailMessage
from jellyfin import main as getJellyfinLatest
from os import environ as osEnviron
import logging as log


################
## Executions ##
################

# Set the loggin level for this entire script set
if osEnviron.get("PYTHON_LOG_LEVEL"):
    PYTHON_LOG_LEVEL = str(osEnviron.get("PYTHON_LOG_LEVEL")).upper()
    log.root.handlers = []
    log.basicConfig(
        level=PYTHON_LOG_LEVEL,
        format="[%(levelname)s] %(message)s",
        handlers=[
            log.FileHandler(filename="output.log", mode='w'),
            log.StreamHandler()
        ]
    )

# Generate the email body for movies
(moviePlainMessage, movieHtmlMessage) = getJellyfinLatest('Movie')

# Generate the email body for series
(seriesPlainMessage, seriesHtmlMessage) = getJellyfinLatest('Series')

# Collate the email bodies for transmission
plainMessage = f"{moviePlainMessage}<br><br>{seriesPlainMessage}"
htmlMessage = f"{movieHtmlMessage}<br><br>{seriesHtmlMessage}"

# Transmit the email with the generated and collated information
sendGmailMessage(plainMessage, htmlMessage)
