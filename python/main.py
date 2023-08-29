from gmail import main as sendGmailMessage
from jellyfin import main as getJellyfinLatest

(moviePlainMessage, movieHtmlMessage) = getJellyfinLatest('Movie')
(seriesPlainMessage, seriesHtmlMessage) = getJellyfinLatest('Series')

plainMessage = f"{moviePlainMessage}<br><br>{seriesPlainMessage}"
htmlMessage = f"{movieHtmlMessage}<br><br>{seriesHtmlMessage}"

sendGmailMessage(plainMessage, htmlMessage)
