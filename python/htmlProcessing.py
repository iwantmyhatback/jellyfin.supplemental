from json import load as loadJson, dumps as dumpsJson
import logging as log


def main(newItemList, queryTypeSpecifics):
    log.debug(
        f'[FUNCTION] htmlProcessing/main( \n{dumpsJson(newItemList, indent=2)}, \n{dumpsJson(queryTypeSpecifics, indent=2)} )')

    (plainMessage, htmlMessage) = generateHeader(
        f'{queryTypeSpecifics.get("name")}(s)', len(newItemList))

    for item in newItemList:
        log.debug(f'[VALUE] item : \n{dumpsJson(item, indent=2)}')

        plainMessage += f"""
            {item.get('title')}\n
            Content Rating: {item.get('content')}\n
            {item.get('community')}
            {item.get('critic')}\n
            Year: {item.get('year')}\n
            Tags: {item.get('tags')}\n
            Genres: {item.get('genres')}\n
            Summary: {item.get('overview')}\n
            Trailer: {item.get('trailer')}\n\n
        """
        log.debug(f'[VALUE] plainMessage : {plainMessage}')

        htmlMessage += (
            f'<div style="display: flex;">'
            f'<div style="flex: 1;margin: 5% 2% 5% 2%;">'
            f"<img style=\"width:25vw;\" src=\"{item.get('image')}\" />"
            f"</div>"
            f'<div style="flex: 5;margin: 8% 2% 8% 2%;">'
            f"<b style=\"font-size:1.5em;\">{item.get('title')}</b>"
            f"<br>"
            f"<b>Year: </b><span>{item.get('year')}</span>"
            f"<br>"
            f"<b>Content Rating: </b><span>{item.get('content')}</span>"
            f"<br>"
            f"<b>Quality Ratings: </b><span>{item.get('community')}</span><span>{item.get('critic')}</span>"
            f"<br>"
            f"<b>Tags: </b><span>{item.get('tags')}</span>"
            f"<br>"
            f"<b>Genres: </b><span>{item.get('genres')}</span>"
            f"<br>"
            f"<b>Summary: </b><span>{item.get('overview')}</span>"
            f"<br><br>"
            f"<a href=\"{item.get('trailer')}\">Trailer</a>"
            f"<br>"
            f"</div>"
            f"<br>"
            f"</div>"
            f"<br>"
        )
        log.debug(f'[VALUE] htmlMessage : {htmlMessage}')
    log.debug(
        f'[RETURN] htmlProcessing/main : \n{plainMessage} \n{htmlMessage}')
    return (plainMessage, htmlMessage)


# generateHeader generates the formatted header for the email in both plaintext and html
# python formatting provider returning them in a tuple

def generateHeader(mediaType, numberOfMovies):
    log.debug(
        f'[FUNCTION] htmlProcessing/generateHeader({mediaType}, {numberOfMovies} )')
    digits = len(str(numberOfMovies))
    mediaTypeLength = len(str(mediaType))
    segmentOne = "+------------+"
    segmentTwo = f"| {numberOfMovies} {mediaType} Updated |"
    segmentThree = "+------------+"
    for i in range(1, (digits + mediaTypeLength), 1):
        segmentOne = segmentOne.replace("-", "--", 1)
        segmentThree = segmentThree.replace("-", "--", 1)
    plainHeader = f"{segmentOne}\n{segmentTwo}\n{segmentThree}\n"
    htmlHeader = f'<h2 style="font-family:courier;">{segmentOne}<br>{segmentTwo}<br>{segmentThree}<br></h2>'
    log.debug(
        f'[RETURN] htmlProcessing/generateHeader : \n{plainHeader} \n{htmlHeader}')
    return (plainHeader, htmlHeader)
