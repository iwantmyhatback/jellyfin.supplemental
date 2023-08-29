from connection import jellyfinConnection
from operator import itemgetter
from utilities import isAquiredThisWeek, stringToDate, replaceEveryNth, posterNotFound
from json import load as loadJson
from requests import get as httpGET
from htmlProcessing import main as generateHtml


info = loadJson(open("configuration/info.json"))


def main(queryType):
    queryTypeSpecifics = parseMediaType(queryType)
    recentlyAddedItems = queryJellyfin(queryTypeSpecifics)
    newItemList = extractItemData(recentlyAddedItems, queryTypeSpecifics)
    (plainMessage, htmlMessage) = generateHtml(newItemList, queryTypeSpecifics)

    return (plainMessage, htmlMessage)


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

        # Timeframe relevance check
        if item.get("DateCreated"):
            relevanceDate = item.get("DateCreated")
        elif item.get("DateLastMediaAdded"):
            relevanceDate = item.get("DateLastMediaAdded")
        else:
            continue
        addedDate = stringToDate(relevanceDate, "%Y-%m-%dT%H:%M:%S.%f")
        if isAquiredThisWeek(addedDate):

            # Title, Overview, Tag List, Genre List
            itemTitle = item.get("Name")
            itemOverview = item.get("Overview")
            itemTagList = ', '.join(item.get("Tags"))
            itemGenreList = ', '.join(item.get("Genres"))

            # Movie Poster URL
            tmdbId = item.get("ProviderIds").get('Tmdb')
            tmdbApiKey = info.get('TMDB').get('API_KEY')
            response = httpGET(
                url=queryTypeSpecifics.get('tmdbUrl').format(
                    tmdbId=tmdbId,
                    apiKey=tmdbApiKey
                )
            )
            responseDict = response.json()

            if responseDict.get('success') == False or len(responseDict.get('posters')) < 1:
                itemPosterUrl = posterNotFound
            else:
                imageFile = responseDict.get('posters')[0].get('file_path')
                itemPosterUrl = baseImageUrl.format(imageId=imageFile)

            # Movie Release Year
            if item.get("PremiereDate"):
                itemPremierDate = stringToDate(
                    item.get("PremiereDate"), "%Y-%m-%dT%H:%M:%S.%f")
                itemYear = itemPremierDate.year
            else:
                itemYear = 0000

            # Content Rating
            if item.get("OfficialRating"):
                itemContentRating = item.get("OfficialRating")
            else:
                itemContentRating = 'Unknown'

            # Critic Rating
            if item.get("CriticRating"):
                itemCriticRating = "Critics: {}% ".format(
                    item.get("CriticRating"))
            else:
                itemCriticRating = ''

            # Community Rating
            if item.get("CommunityRating"):
                withCritic = '& ' if itemCriticRating != '' else ''
                roundedRating = round(float(item.get("CommunityRating")), 1)
                itemCommunityRating = "Community: {}/10 {}".format(
                    roundedRating, withCritic)
            else:
                itemCommunityRating = ''

            # Trailer URL
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
