from datetime import *

# isAquiredThisWeek takes in a datetime and returns Boolean indicating whether or not the date
# is within the previous 1 week (7 days)


def isAquiredThisWeek(dateAdded):
    now = datetime.now()
    return (now - dateAdded).days <= 7


# stringToDate takes an input String and the date format or parsing the input string into
# a datetime object see: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior


def stringToDate(dateString, dateFormat):
    return datetime.strptime(dateString[:-2], dateFormat)


# replaceEveryNth takes a string (analysisString) and seatches it for a substring (substitutionTarget)
# and replaces every (nth) instance of the substring with a replacement substring (targetReplacement)


def replaceEveryNth(analysisString, substitutionTarget, targetReplacement, nth):
    find = analysisString.find(substitutionTarget)
    # loop util we find no match
    i = 1
    while find != -1:
        # if i  is equal to nth we found nth matches so replace
        if i == nth:
            analysisString = (
                analysisString[:find]
                + targetReplacement
                + analysisString[find + len(substitutionTarget):]
            )
            i = 0
        # find + len(substitutionTarget) + 1 means we start after the last match
        find = analysisString.find(
            substitutionTarget, find + len(substitutionTarget) + 1
        )
        i += 1
    return analysisString


# generateHeader generates the formatted header for the email in both plaintext and html
# python formatting provider returning them in a tuple


def generateHeader(mediaType, numberOfMovies):
    digits = len(str(numberOfMovies))
    mediaTypeLength = len(str(mediaType))
    segmentOne = "+--------------------+"
    segmentTwo = f"|{numberOfMovies} {mediaType} Updated This Week|"
    segmentThree = "+--------------------+"
    for i in range(1, (digits + mediaTypeLength), 1):
        segmentOne = segmentOne.replace("-", "--", 1)
        segmentThree = segmentThree.replace("-", "--", 1)
    plainHeader = f"{segmentOne}\n{segmentTwo}\n{segmentThree}\n"
    htmlHeader = f'<h2 style="font-family:courier;">{segmentOne}<br>{segmentTwo}<br>{segmentThree}<br></h2>'
    return (plainHeader, htmlHeader)
