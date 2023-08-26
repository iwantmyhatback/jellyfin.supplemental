import gmail
from jellyfinMovies import main as jellyfinMovies
from jellyfinSeries import main as jellyfinSeries

(moviePlainMessage, movieHtmlMessage) = jellyfinMovies()
(seriesPlainMessage, seriesHtmlMessage) = jellyfinSeries()

plainMessage = f"{moviePlainMessage}<br><br>{seriesPlainMessage}"
htmlMessage = f"{movieHtmlMessage}<br><br>{seriesHtmlMessage}"

gmail.main(plainMessage, htmlMessage)
