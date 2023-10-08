from datetime import *
from urllib.parse import urlparse
import logging as log
from os import environ as osEnviron


#################
## Definitions ##
#################

# isAquiredWithinThreshold() Takes in a datetime and returns Boolean indicating whether or not the date is within the threshold defined in configuration/environment.properties (defaults to 7 days)
def isAquiredWithinThreshold(dateAdded):
    dayThreshold = int(osEnviron.get("DAY_THRESHOLD")) or 7
    log.debug(f'[FUNCTION] utilities/isAquiredWithinThreshold({dateAdded})')
    now = datetime.now()
    withinThreshold = (now - dateAdded).days <= dayThreshold
    log.debug(
        f'[RETURN] isAquiredWithinThreshold : {withinThreshold}')
    return withinThreshold


# stringToDate() Takes an input String and the date format or parsing the input string into a datetime object
# see: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
def stringToDate(dateString, dateFormat):
    log.debug(
        f'[FUNCTION] utilities/stringToDate({dateString}, {dateFormat})')
    returnDate = datetime.strptime(dateString[:-2], dateFormat)
    log.debug(f'[RETURN] stringToDate : {returnDate}')
    return returnDate


# replaceEveryNth() Takes a string (analysisString) and seatches it for a substring (substitutionTarget) and replaces every (nth) instance of the substring with a replacement substring (targetReplacement)
def replaceEveryNth(analysisString, substitutionTarget, targetReplacement, nth):
    log.debug(
        f'[FUNCTION] utilities/replaceEveryNth({analysisString}, {substitutionTarget}, {targetReplacement}, {nth})')
    find = analysisString.find(substitutionTarget)

    i = 1
    while find != -1:
        if i == nth:
            analysisString = (
                analysisString[:find]
                + targetReplacement
                + analysisString[find + len(substitutionTarget):]
            )
            i = 0

        find = analysisString.find(
            substitutionTarget, find + len(substitutionTarget) + 1
        )

        i += 1

    log.debug(f'[RETURN] utilities/replaceEveryNth : {analysisString}')
    return analysisString


# getLastUrlSegment taks a url string and returns the last segment
def getLastUrlSegment(url):
    log.debug(f'[FUNCTION] utilities/getLastUrlSegment({url})')
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split("/")
    last_segment = path_segments[-1] if path_segments else ""
    log.debug(f'[RETURN] utilities/getLastUrlSegment : {last_segment}')
    return last_segment
