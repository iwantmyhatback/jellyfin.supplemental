from json import dumps as dumpsJson
import logging as log


#################
## Definitions ##
#################

# generateHeader() Generates the formatted header for the email in both plaintext and html
def generateHeader(mediaType, numberOfMovies):
    log.debug(
        f'[FUNCTION] htmlProcessing/generateHeader({mediaType}, {numberOfMovies})')
    digits = len(str(numberOfMovies))
    mediaTypeLength = len(str(mediaType))
    segmentOne = "+------------+"
    segmentTwo = f"| {numberOfMovies} {mediaType} Updated |"
    segmentThree = "+------------+"
    for _ in range(1, (digits + mediaTypeLength), 1):
        segmentOne = segmentOne.replace("-", "--", 1)
        segmentThree = segmentThree.replace("-", "--", 1)
    plainHeader = f"{segmentOne}\n{segmentTwo}\n{segmentThree}\n"
    htmlHeader = f'''
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: clamp(4px, 0.8vw, 8px); margin-bottom: clamp(12px, 2vw, 20px);">
        <tr>
            <td style="padding: clamp(15px, 3vw, 30px); text-align: center;">
                <h1 style="color: white; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: clamp(20px, 4vw, 32px); font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    {numberOfMovies} New {mediaType}
                </h1>
                <p style="color: rgba(255,255,255,0.9); margin: clamp(6px, 1vw, 10px) 0 0 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: clamp(12px, 2vw, 16px);">
                    Recently added to Trisflix
                </p>
            </td>
        </tr>
    </table>
    '''
    log.debug(
        f'[RETURN] htmlProcessing/generateHeader : \n{plainHeader} \n{htmlHeader}')
    return (plainHeader, htmlHeader)


################
## Executions ##
################

# main() Performs the functionality of this file. Processing the Jellyfin data into Plain Text and HTML email bodies
def main(newItemList, queryTypeSpecifics):
    log.debug(
        f'[FUNCTION] htmlProcessing/main(\n{dumpsJson(newItemList, indent=2)}, \n{dumpsJson(queryTypeSpecifics, indent=2)})')

    (plainMessage, htmlMessage) = generateHeader(
        f'{queryTypeSpecifics.get("name")}(s)', len(newItemList))

    # Wrap content in responsive container with viewport meta
    htmlMessage = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <style type="text/css">
            body {{ font-size: clamp(12px, 1.8vw, 14px); }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f5f5f5;">
            <tr>
                <td align="center" style="padding: clamp(10px, 2vw, 20px);">
                    <table width="100%" style="max-width: 1200px;" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td>
                                {htmlMessage}
    '''

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

        htmlMessage += f'''
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: white; border-radius: clamp(6px, 1.2vw, 12px); margin-bottom: clamp(12px, 2vw, 20px); box-shadow: 0 2px 6px rgba(0,0,0,0.1); overflow: hidden;">
                <tr>
                    <td width="185" valign="middle" style="width: 185px; overflow: hidden; border-top-left-radius: clamp(6px, 1.2vw, 12px); border-bottom-left-radius: clamp(6px, 1.2vw, 12px);">
                        <img src="{item.get('image')}" alt="{item.get('title')}" style="display: block; width: 185px; height: auto;" />
                    </td>
                    <td valign="top" style="padding: clamp(12px, 1.5vw, 20px); overflow: hidden;">
                        <h2 style="margin: 0 0 clamp(4px, 0.6vw, 8px) 0; font-size: clamp(14px, 1.8vw, 20px); font-weight: 600; color: #1a1a1a; line-height: 1.2; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                            {item.get('title')}
                        </h2>

                        <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom: clamp(4px, 0.6vw, 8px);">
                            <tr>
                                <td style="padding: 2px clamp(6px, 0.8vw, 10px); background-color: #667eea; color: white; border-radius: clamp(6px, 1vw, 12px); font-size: clamp(10px, 1.2vw, 12px); font-weight: 500; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                                    {item.get('year')}
                                </td>
                                <td style="width: clamp(3px, 0.4vw, 6px);"></td>
                                <td style="padding: 2px clamp(6px, 0.8vw, 10px); background-color: #f59e0b; color: white; border-radius: clamp(6px, 1vw, 12px); font-size: clamp(10px, 1.2vw, 12px); font-weight: 500; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                                    {item.get('content')}
                                </td>
                            </tr>
                        </table>

                        {f'<p style="margin: 0 0 clamp(3px, 0.4vw, 6px) 0; color: #4a5568; font-size: clamp(10px, 1.2vw, 13px); line-height: 1.4; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;"><strong style="color: #2d3748;">Ratings:</strong> {item.get("community")} {item.get("critic")}</p>' if item.get('community') or item.get('critic') else ''}

                        {f'<p style="margin: 0 0 clamp(3px, 0.4vw, 6px) 0; color: #4a5568; font-size: clamp(10px, 1.2vw, 13px); line-height: 1.4; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;"><strong style="color: #2d3748;">Genres:</strong> {item.get("genres")}</p>' if item.get('genres') else ''}

                        {f'<p style="margin: 0 0 clamp(3px, 0.4vw, 6px) 0; color: #4a5568; font-size: clamp(10px, 1.2vw, 13px); line-height: 1.4; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;"><strong style="color: #2d3748;">Tags:</strong> {item.get("tags")}</p>' if item.get('tags') else ''}

                        <p style="margin: 0 0 clamp(4px, 0.6vw, 8px) 0; color: #4a5568; font-size: clamp(10px, 1.2vw, 13px); line-height: 1.4; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                            {item.get('overview')}
                        </p>

                        <table cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: clamp(3px, 0.5vw, 5px);">
                                    <a href="{item.get('trailer')}" style="display: inline-block; padding: clamp(5px, 0.7vw, 8px) clamp(10px, 1.4vw, 18px); color: white; text-decoration: none; font-weight: 500; font-size: clamp(10px, 1.2vw, 13px); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                                        ▶ Watch Trailer
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        '''
    log.debug(f'[VALUE] htmlMessage : {htmlMessage}')

    # Close containers
    htmlMessage += '''
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    '''

    log.debug(
        f'[RETURN] htmlProcessing/main : \n{plainMessage} \n{htmlMessage}')
    return (plainMessage, htmlMessage)
