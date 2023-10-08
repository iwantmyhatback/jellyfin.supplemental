from connection import jellyfinConnection
from operator import itemgetter
from utilities import isAquiredThisWeek, stringToDate, replaceEveryNth, getLastUrlSegment
from json import load as loadJson, dumps as dumpsJson
from requests import get as httpGET
from htmlProcessing import main as generateHtml
import logging as log

info = loadJson(open("configuration/info.json"))
log.debug(f'[LOAD] configuration/info.json : \n{dumpsJson(info, indent=2)}')

client = jellyfinConnection()


def main(queryType):
    log.debug(f'[FUNCTION] jellyfin/main({queryType})')
    queryTypeSpecifics = parseMediaType(queryType)
    recentlyAddedItems = queryJellyfin(queryTypeSpecifics)
    newItemList = extractItemData(recentlyAddedItems, queryTypeSpecifics)
    (plainMessage, htmlMessage) = generateHtml(newItemList, queryTypeSpecifics)
    log.debug(
        f'[RETURN] jellyfin/main : \nPLAIN:\n{plainMessage} \nHTML:\n{htmlMessage}')
    return (plainMessage, htmlMessage)


def parseMediaType(queryType):
    log.debug(f'[FUNCTION] jellyfin/parseMediaType({queryType})')
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
            'fields': ['DateCreated', *defaultFields]
        },
        'Series': {
            'name': 'Series',
            'mediaTypesList': ['Series'],
            'fields': ['DateLastMediaAdded', *defaultFields]
        }
    }

    validTypes = mediaSpecifics.keys()
    if queryType not in validTypes:
        log.error(
            f'[ERROR] queryType passed to jellyfinLatest.main() must be one of {validTypes}')
        raise ValueError()

    log.debug(
        f'[RETURN] jellyfin/parseMediaType : \n{dumpsJson(mediaSpecifics.get(queryType), indent=2)}')
    return mediaSpecifics.get(queryType)


def queryJellyfin(queryTypeSpecifics):
    log.debug(f'[FUNCTION] jellyfin/queryJellyfin({queryTypeSpecifics})')

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
        log.error(
            f'[ERROR] There was an error querying latest {queryTypeSpecifics.get("name")}')
        raise RuntimeError()
    log.debug(
        f'[RETURN] jellyfin/queryJellyfin :\n{dumpsJson(recentlyAddedItems, indent=2)}')
    return recentlyAddedItems


def extractItemData(recentlyAddedItems, queryTypeSpecifics):
    log.debug(
        f'[FUNCTION] jellyfin/extractItemData(\n{dumpsJson(recentlyAddedItems, indent=2)}, \n{dumpsJson(queryTypeSpecifics, indent=2)})')
    newItemList = []
    baseYoutube = "https://www.youtube.com/watch?v={trailerId}"

    for item in recentlyAddedItems:
        log.debug(f'[VALUE] item : \n{dumpsJson(item, indent=2)}')

        # Timeframe relevance check
        if item.get("DateCreated"):
            relevanceDate = item.get("DateCreated")
            log.debug(f'[VALUE] item.DateCreated : {relevanceDate}')

        elif item.get("DateLastMediaAdded"):
            relevanceDate = item.get("DateLastMediaAdded")
            log.debug(f'[VALUE] item.DateLastMediaAdded : {relevanceDate}')

        else:
            log.warning(
                f'[VALUE] item.name: {item.get("Name")} has no item.DateCreated OR item.DateLastMediaAdded')
            continue

        addedDate = stringToDate(relevanceDate, "%Y-%m-%dT%H:%M:%S.%f")

        if isAquiredThisWeek(addedDate):

            # Title, Overview, Tag List, Genre List
            itemTitle = item.get("Name")
            log.debug(f'[VALUE] itemTitle : {itemTitle}')

            itemOverview = item.get("Overview")
            log.debug(f'[VALUE] itemOverview : {itemOverview}')

            itemTagList = ', '.join(item.get("Tags"))
            log.debug(f'[VALUE] itemTagList : {itemTagList}')

            itemGenreList = ', '.join(item.get("Genres"))
            log.debug(f'[VALUE] itemGenreList : {itemGenreList}')

            # Movie Poster URL
            itemPosterUrl = getRemoteImage(item)
            log.debug(f'[VALUE] itemPosterUrl : {itemPosterUrl}')

            # Movie Release Year
            if item.get("PremiereDate"):
                itemPremierDate = stringToDate(
                    item.get("PremiereDate"), "%Y-%m-%dT%H:%M:%S.%f")
                itemYear = itemPremierDate.year

            else:
                log.debug(
                    f'[VALUE] item.name: {item.get("Name")} has no item.PremiereDate')
                itemYear = 0000

            log.debug(f'[VALUE] itemYear : {itemYear}')

            # Content Rating
            if item.get("OfficialRating"):
                itemContentRating = item.get("OfficialRating")

            else:
                itemContentRating = 'Unknown'
                log.debug(
                    f'[VALUE] item.name: {item.get("Name")} has no item.OfficialRating')

            log.debug(f'[VALUE] itemContentRating : {itemContentRating}')

            # Critic Rating
            if item.get("CriticRating"):
                itemCriticRating = "Critics: {}% ".format(
                    item.get("CriticRating"))

            else:
                itemCriticRating = ''
                log.debug(
                    f'[VALUE] item.name: {item.get("Name")} has no item.CriticRating')

            log.debug(f'[VALUE] itemCriticRating : {itemCriticRating}')

            # Community Rating
            if item.get("CommunityRating"):
                withCritic = '& ' if itemCriticRating != '' else ''
                roundedRating = round(float(item.get("CommunityRating")), 1)
                itemCommunityRating = "Community: {}/10 {}".format(
                    roundedRating, withCritic)

            else:
                itemCommunityRating = ''
                log.debug(
                    f'[VALUE] item.name: {item.get("Name")} has no item.CommunityRating')

            log.debug(f'[VALUE] itemCommunityRating : {itemCommunityRating}')

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

            else:
                log.debug(
                    f'[VALUE] item.name: {item.get("Name")} has no item.RemoteTrailers')
                log.debug(
                    f'[VALUE] using default itemTrailerUrl (rickroll) : {itemTrailerUrl}')

            log.debug(f'[VALUE] itemTrailerUrl : {itemTrailerUrl}')

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
            log.debug(
                f'[VALUE] appended : \n{dumpsJson(newItemList[-1])} to newItemList')

    newItemList = sorted(newItemList, key=itemgetter("year"), reverse=True)
    log.debug(
        f'[RETURN] jellyfin/extractItemData : \n{dumpsJson(newItemList)}')
    return newItemList


def getRemoteImage(item):
    log.debug(
        f'[FUNCTION] jellyfin/getRemoteImage(\n{dumpsJson(item, indent=2)})')
    baseImageUrl = "http://image.tmdb.org/t/p/w185/{imageId}"
    itemId = item.get('Id')

    response = client.jellyfin.items(
        handler=f"/{itemId}/RemoteImages/",
        params={
            'providerName': 'TheMovieDb',
            'type': 'Primary',
            'includeAllLanguages': False
        }
    )

    finalImage = {
        'imageFile': '',
        'rating': -1,
        'votes': -1,
    }

    for image in response.get('Images'):

        if image.get('CommunityRating') > finalImage.get('rating') and image.get('VoteCount') >= finalImage.get('votes'):
            imageFile = getLastUrlSegment(image.get('Url'))
            imageRating = image.get('CommunityRating')
            imageVotes = image.get('VoteCount')

            finalImage.update(imageFile=imageFile)
            finalImage.update(rating=imageRating)
            finalImage.update(votes=imageVotes)

    if finalImage.get('imageFile') == '':
        notFoundUrl = 'https://www.movienewz.com/img/films/poster-holder.jpg'
        log.debug(f'[RETURN] jellyfin/getRemoteImage : {notFoundUrl}')
        return notFoundUrl

    else:
        formattedUrl = baseImageUrl.format(imageId=imageFile)
        log.debug(f'[RETURN] jellyfin/getRemoteImage : {formattedUrl}')
        return formattedUrl
