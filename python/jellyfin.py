from connection import jellyfinConnection
from operator import itemgetter
from utilities import isAquiredThisWeek, stringToDate, replaceEveryNth, generateHeader, posterNotFound
from json import load as loadJson
from requests import get as httpGET

# Load JSON from configuration file
info = loadJson(open("configuration/info.json"))

# Perfrom the Query, processing, and HTML generation


def main(queryType):
    queryTypeSpecifics = parseMediaType(queryType)
    recentlyAddedItems = queryJellyfin(queryTypeSpecifics)
    newItemList = extractItemData(recentlyAddedItems, queryTypeSpecifics)
    (plainMessage, htmlMessage) = generateHtml(newItemList, queryTypeSpecifics)

    return (plainMessage, htmlMessage)

#


def parseMediaType(queryType):
    defaultFields = ['Tags',
                     'Genres',
                     'ProviderIds',
                     'RemoteTrailers',
                     'Overview'
                     ]
    mediaSpecifics = {
        'Movie': {
            'name': 'Movie',
            'mediaTypesList': ['Movie'],
            'tmdbUrl': "https://api.themoviedb.org/3/movie/{tmdbId}/images?language=en&api_key={apiKey}",
            'fields': ['DateCreated', *defaultFields]
        },
        'Series': {
            'name': 'Series',
            'mediaTypesList': ['Series'],
            'tmdbUrl': "https://api.themoviedb.org/3/tv/{tmdbId}/images?language=en&api_key={apiKey}",
            'fields': ['DateLastMediaAdded', *defaultFields]
        }
    }

    validTypes = mediaSpecifics.keys()
    if queryType not in validTypes:
        raise ValueError(
            f"[ERROR] queryType passed to jellyfinLatest.main() must be one of {validTypes}")

    return mediaSpecifics.get(queryType)


def queryJellyfin(queryTypeSpecifics):
    client = jellyfinConnection()

    try:
        recentlyAddedItems = client.jellyfin.user_items(
            handler="/Latest",
            params={
                'fields': queryTypeSpecifics.get('fields'),
                'includeItemTypes': queryTypeSpecifics.get('mediaTypesList'),
                'limit': 1000
            }
        )
    except:
        raise RuntimeError(
            f'[ERROR] There was an error querying latest {queryTypeSpecifics.get("name")}')

    return recentlyAddedItems


def extractItemData(recentlyAddedItems, queryTypeSpecifics):
    newItemList = []
    baseImageUrl = "http://image.tmdb.org/t/p/w185/{imageId}"
    baseYoutube = "https://www.youtube.com/watch?v={trailerId}"

    for item in recentlyAddedItems:
        # Check if the item was added this week
        if item.get("DateCreated"):
            relevanceDate = item.get("DateCreated")
        elif item.get("DateLastMediaAdded"):
            relevanceDate = item.get("DateLastMediaAdded")
        else:
            continue

        addedDate = stringToDate(relevanceDate, "%Y-%m-%dT%H:%M:%S.%f")
        if isAquiredThisWeek(addedDate):
            # Parse uprocessed Item values : (Title, Overview, Tag List, Genre List)
            itemTitle = item.get("Name")
            itemOverview = item.get("Overview")
            itemTagList = ', '.join(item.get("Tags"))
            itemGenreList = ', '.join(item.get("Genres"))

            # Parse Movie Poster URL
            tmdbId = item.get("ProviderIds").get('Tmdb')
            tmdbApiKey = info.get('TMDB').get('API_KEY')
            response = httpGET(
                url=queryTypeSpecifics.get('tmdbUrl').format(
                    tmdbId=tmdbId,
                    apiKey=tmdbApiKey
                )
            )
            responseDict = response.json()

            # Bail out for current item if the poster is missing
            if responseDict.get('success') == False or len(responseDict.get('posters')) < 1:
                itemPosterUrl = posterNotFound
            else:
                imageFile = responseDict.get('posters')[0].get('file_path')
                itemPosterUrl = baseImageUrl.format(imageId=imageFile)

            # Parse Movie Release Year
            if item.get("PremiereDate"):
                itemPremierDate = stringToDate(
                    item.get("PremiereDate"), "%Y-%m-%dT%H:%M:%S.%f")
                itemYear = itemPremierDate.year
            else:
                itemYear = 0000

            # Parse Content Rating
            if item.get("OfficialRating"):
                itemContentRating = item.get("OfficialRating")
            else:
                itemContentRating = 'Unknown'

            # Parse Critic Rating
            if item.get("CriticRating"):
                itemCriticRating = "Critics: {}% ".format(
                    item.get("CriticRating"))
            else:
                itemCriticRating = ''

            # Parse Community Rating
            if item.get("CommunityRating"):
                withCritic = '& ' if itemCriticRating != '' else ''
                roundedRating = round(float(item.get("CommunityRating")), 1)
                itemCommunityRating = "Community: {}/10 {}".format(
                    roundedRating, withCritic)
            else:
                itemCommunityRating = ''

            # Parse Trailer URL
            itemTrailerUrl = baseYoutube.format(trailerId='dQw4w9WgXcQ')
            if len(item.get("RemoteTrailers")) > 0:
                trailerElement = item.get("RemoteTrailers")[0]
                trailerUrl = trailerElement.get('Url')

                if 'watch?v=' in trailerUrl:
                    trailerId = trailerUrl.rsplit('watch?v=', 1)[-1]
                    itemTrailerUrl = baseYoutube.format(trailerId=trailerId)
                elif 'video_id=' in trailerUrl:
                    trailerId = trailerUrl.rsplit('video_id=', 1)[-1]
                    itemTrailerUrl = baseYoutube.format(trailerId=trailerId)

            newItemList.append(
                {
                    "title": itemTitle,
                    "overview": replaceEveryNth(itemOverview, " ", " \n", 15),
                    "tags": itemTagList,
                    "genres": itemGenreList,
                    "image": itemPosterUrl,
                    "year": itemYear,
                    "content": itemContentRating,
                    "critic": itemCriticRating,
                    "community": itemCommunityRating,
                    "trailer": itemTrailerUrl,
                }
            )
    newItemList = sorted(newItemList, key=itemgetter("year"), reverse=True)
    return newItemList


def generateHtml(newItemList, queryTypeSpecifics):
    (plainMessage, htmlMessage) = generateHeader(
        f'{queryTypeSpecifics.get("name")}(s)', len(newItemList))

    for item in newItemList:
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

    return (plainMessage, htmlMessage)
