from gmail import main as sendGmailMessage
from jellyfin import main as getJellyfinLatest
from os import environ as osEnviron
import logging as log

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


(moviePlainMessage, movieHtmlMessage) = getJellyfinLatest('Movie')
(seriesPlainMessage, seriesHtmlMessage) = getJellyfinLatest('Series')

plainMessage = f"{moviePlainMessage}<br><br>{seriesPlainMessage}"
htmlMessage = f"{movieHtmlMessage}<br><br>{seriesHtmlMessage}"

sendGmailMessage(plainMessage, htmlMessage)

exit(0)
