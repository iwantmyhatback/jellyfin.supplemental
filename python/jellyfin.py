from operator import itemgetter
from utilities import isAquiredWithinThreshold, replaceEveryNth, getLastUrlSegment
from json import load as loadJson, dumps as dumpsJson, dump as dumpJson
from htmlProcessing import main as generateHtml
from os import environ as osEnviron, path as osPath
import logging as log

import jellyfin_api
from jellyfin_api.api.user_api import UserApi
from jellyfin_api.api.items_api import ItemsApi
from jellyfin_api.api.remote_image_api import RemoteImageApi


#################
## Definitions ##
#################

# Check whether we want to use secondary JSON file (mostly used for testing on a secondary machine)
REMOTE_CONNECTION = str(osEnviron.get("REMOTE_CONNECTION")).upper()
DEVICE = osEnviron.get("DEVICE") or "defaultDevice"
DEVICE_ID = osEnviron.get("DEVICE_ID") or "defaultDeviceId"

# Load the appropriate JSON file of configurations
if REMOTE_CONNECTION in ["YES", "TRUE"]:
    log.info(
        f'[ENV] REMOTE_CONNECTION={REMOTE_CONNECTION} passed in environment ..........')
    whichInfoFile = "info.remote.json"
    infoFile = open(f"configuration/{whichInfoFile}")

else:
    whichInfoFile = "info.json"
    infoFile = open(f"configuration/{whichInfoFile}")

info = loadJson(infoFile)
log.debug(
    f'[LOAD] configuration/{whichInfoFile} : \n{dumpsJson(info, indent=2)}')


# jellyfinConnection() Authorizes with Jellyfin, creates a credential file, and returns a client object
def jellyfinConnection():
    log.debug('[FUNCTION] connection/jellyfinConnection()')
    JELLYFIN = info.get("JELLYFIN")
    SERVER_URL = JELLYFIN.get("SERVER_URL")
    PORT = JELLYFIN.get("PORT")
    USERNAME = JELLYFIN.get("USERNAME")
    PASSWORD = JELLYFIN.get("PASSWORD")
    CREDENTIAL_LOCATION = JELLYFIN.get("CREDENTIAL_LOCATION")
    CLIENT_SECRET_FILE = JELLYFIN.get("CLIENT_SECRET_FILE")
    CREDENTIAL_FILE = f"{CREDENTIAL_LOCATION}/{CLIENT_SECRET_FILE}"

    configuration = jellyfin_api.Configuration(host=f"{SERVER_URL}:{PORT}")

    if osPath.isfile(CREDENTIAL_FILE):
        credentials = loadJson(open(CREDENTIAL_FILE))
        token = credentials["AccessToken"]
        user_id = credentials["UserId"]
    else:
        # Initial auth — the authenticate endpoint doesn't include auth settings
        # in the generated client, so we pass the header manually
        auth_header = (
            'MediaBrowser Client="jellyfin.supplemental", '
            'Device="administratorsMachine", '
            'DeviceId="adminMach", '
            'Version="0.0.1"'
        )
        api_client = jellyfin_api.ApiClient(configuration)
        auth_api = UserApi(api_client)
        result = auth_api.authenticate_user_by_name(
            jellyfin_api.AuthenticateUserByName(username=USERNAME, pw=PASSWORD),
            _headers={'Authorization': auth_header}
        )
        token = result.access_token
        user_id = str(result.user.id)
        with open(CREDENTIAL_FILE, 'w', encoding='utf-8') as f:
            dumpJson({"AccessToken": token, "UserId": user_id, "username": USERNAME}, f, indent=4)

    # Set auth header with token for all subsequent calls
    configuration.api_key['CustomAuthentication'] = (
        f'MediaBrowser Token="{token}", '
        f'Client="jellyfin.supplemental", '
        f'Device="{DEVICE}", '
        f'DeviceId="{DEVICE_ID}", '
        f'Version="1.0.0"'
    )
    api_client = jellyfin_api.ApiClient(configuration)
    log.debug(f'[RETURN] connection/jellyfinConnection : {api_client}')
    return api_client, user_id


# parseMediaType() Returns the specifics for query depending on the type of media (TV and Movies are determined to be new differently)
def parseMediaType(queryType):
    log.debug(f'[FUNCTION] jellyfin/parseMediaType({queryType})')
    defaultFields = [jellyfin_api.ItemFields.TAGS,
                     jellyfin_api.ItemFields.GENRES,
                     jellyfin_api.ItemFields.PROVIDERIDS,
                     jellyfin_api.ItemFields.REMOTETRAILERS,
                     jellyfin_api.ItemFields.OVERVIEW]
    mediaSpecifics = {
        'Movie': {
            'name': 'Movie',
            'mediaTypesList': [jellyfin_api.BaseItemKind.MOVIE],
            'fields': [jellyfin_api.ItemFields.DATECREATED, *defaultFields],
            'sortBy': [jellyfin_api.ItemSortBy.DATECREATED]
        },
        'Series': {
            'name': 'Series',
            'mediaTypesList': [jellyfin_api.BaseItemKind.SERIES],
            'fields': [jellyfin_api.ItemFields.DATELASTMEDIAADDED, *defaultFields],
            'sortBy': [jellyfin_api.ItemSortBy.DATELASTCONTENTADDED]
        }
    }

    validTypes = mediaSpecifics.keys()
    if queryType not in validTypes:
        log.error(
            f'[ERROR] queryType passed to jellyfinLatest.main() must be one of {validTypes}')
        raise ValueError()

    log.debug(
        f'[RETURN] jellyfin/parseMediaType : {mediaSpecifics.get(queryType)}')
    return mediaSpecifics.get(queryType)


# queryJellyfin() Gets all the recently added media of the specified type
def queryJellyfin(queryTypeSpecifics):
    log.debug(f'[FUNCTION] jellyfin/queryJellyfin({queryTypeSpecifics})')

    try:
        items_api = ItemsApi(api_client)
        result = items_api.get_items(
            user_id=user_id,
            fields=queryTypeSpecifics.get('fields'),
            include_item_types=queryTypeSpecifics.get('mediaTypesList'),
            sort_by=queryTypeSpecifics.get('sortBy'),
            sort_order=[jellyfin_api.SortOrder.DESCENDING],
            recursive=True,
            limit=50,
            _request_timeout=30
        )
        recentlyAddedItems = result.items or []
    except Exception:
        log.error(
            f'[ERROR] There was an error querying latest {queryTypeSpecifics.get("name")}')
        raise RuntimeError()
    log.debug(
        f'[RETURN] jellyfin/queryJellyfin : {len(recentlyAddedItems)} items')
    return recentlyAddedItems


# extractItemData() extracts the data for the email from the Jellyfin response data and formats it into a list of uniform objects
def extractItemData(recentlyAddedItems, queryTypeSpecifics):
    log.debug(
        f'[FUNCTION] jellyfin/extractItemData({len(recentlyAddedItems)} items)')
    newItemList = []
    baseYoutube = "https://www.youtube.com/watch?v={trailerId}"

    for item in recentlyAddedItems:
        log.debug(f'[VALUE] item : \n{item.model_dump_json(indent=2)}')

        # Timeframe relevance check
        if item.date_created:
            relevanceDate = item.date_created
            log.debug(f'[VALUE] item.date_created : {relevanceDate}')

        elif item.date_last_media_added:
            relevanceDate = item.date_last_media_added
            log.debug(f'[VALUE] item.date_last_media_added : {relevanceDate}')

        else:
            log.warning(
                f'[VALUE] item.name: {item.name} has no date_created OR date_last_media_added')
            continue

        # date_created and date_last_media_added are already datetime objects
        addedDate = relevanceDate.replace(tzinfo=None)

        if isAquiredWithinThreshold(addedDate):

            # Title, Overview, Tag List, Genre List
            itemTitle = item.name
            log.debug(f'[VALUE] itemTitle : {itemTitle}')

            itemOverview = item.overview
            log.debug(f'[VALUE] itemOverview : {itemOverview}')

            itemTagList = ', '.join(item.tags) if item.tags else ''
            log.debug(f'[VALUE] itemTagList : {itemTagList}')

            itemGenreList = ', '.join(item.genres) if item.genres else ''
            log.debug(f'[VALUE] itemGenreList : {itemGenreList}')

            # Movie Poster URL
            itemPosterUrl = getRemoteImage(item)
            log.debug(f'[VALUE] itemPosterUrl : {itemPosterUrl}')

            # Movie Release Year
            if item.premiere_date:
                itemYear = item.premiere_date.year

            else:
                log.debug(
                    f'[VALUE] item.name: {item.name} has no premiere_date')
                itemYear = 0000

            log.debug(f'[VALUE] itemYear : {itemYear}')

            # Content Rating
            if item.official_rating:
                itemContentRating = item.official_rating

            else:
                itemContentRating = 'Unknown'
                log.debug(
                    f'[VALUE] item.name: {item.name} has no official_rating')

            log.debug(f'[VALUE] itemContentRating : {itemContentRating}')

            # Critic Rating
            if item.critic_rating:
                itemCriticRating = "Critics: {}% ".format(
                    item.critic_rating)

            else:
                itemCriticRating = ''
                log.debug(
                    f'[VALUE] item.name: {item.name} has no critic_rating')

            log.debug(f'[VALUE] itemCriticRating : {itemCriticRating}')

            # Community Rating
            if item.community_rating:
                withCritic = '& ' if itemCriticRating != '' else ''
                roundedRating = round(float(item.community_rating), 1)
                itemCommunityRating = "Community: {}/10 {}".format(
                    roundedRating, withCritic)

            else:
                itemCommunityRating = ''
                log.debug(
                    f'[VALUE] item.name: {item.name} has no community_rating')

            log.debug(f'[VALUE] itemCommunityRating : {itemCommunityRating}')

            # Trailer URL
            itemTrailerUrl = baseYoutube.format(trailerId='dQw4w9WgXcQ')
            if item.remote_trailers and len(item.remote_trailers) > 0:
                trailerElement = item.remote_trailers[0]
                trailerUrl = trailerElement.url

                if trailerUrl and 'watch?v=' in trailerUrl:
                    trailerId = trailerUrl.rsplit('watch?v=', 1)[-1]
                    itemTrailerUrl = baseYoutube.format(trailerId=trailerId)

                elif trailerUrl and 'video_id=' in trailerUrl:
                    trailerId = trailerUrl.rsplit('video_id=', 1)[-1]
                    itemTrailerUrl = baseYoutube.format(trailerId=trailerId)

            else:
                log.debug(
                    f'[VALUE] item.name: {item.name} has no remote_trailers')
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


# getRemoteImage() gets a poster image from TMDB
def getRemoteImage(item):
    log.debug(
        f'[FUNCTION] jellyfin/getRemoteImage({item.name})')
    baseImageUrl = "http://image.tmdb.org/t/p/w185/{imageId}"

    img_api = RemoteImageApi(api_client)
    response = img_api.get_remote_images(
        item_id=item.id,
        type=jellyfin_api.ImageType.PRIMARY,
        provider_name='TheMovieDb',
        include_all_languages=False
    )

    finalImage = {
        'imageFile': '',
        'rating': -1,
        'votes': -1,
    }

    for image in response.images:

        if image.community_rating > finalImage.get('rating') and image.vote_count >= finalImage.get('votes'):
            imageFile = getLastUrlSegment(image.url)
            imageRating = image.community_rating
            imageVotes = image.vote_count

            finalImage.update(imageFile=imageFile)
            finalImage.update(rating=imageRating)
            finalImage.update(votes=imageVotes)

    if finalImage.get('imageFile') == '':
        notFoundUrl = 'https://www.movienewz.com/img/films/poster-holder.jpg'
        log.debug(f'[RETURN] jellyfin/getRemoteImage : {notFoundUrl}')
        return notFoundUrl

    else:
        formattedUrl = baseImageUrl.format(imageId=finalImage.get('imageFile'))
        log.debug(f'[RETURN] jellyfin/getRemoteImage : {formattedUrl}')
        return formattedUrl


################
## Executions ##
################

api_client, user_id = jellyfinConnection()


# main() Performs the functionality of this file. Query Jellyfin for infomation, extract the data, and trandform it into emailable format
def main(queryType):
    log.debug(f'[FUNCTION] jellyfin/main({queryType})')
    queryTypeSpecifics = parseMediaType(queryType)
    recentlyAddedItems = queryJellyfin(queryTypeSpecifics)
    newItemList = extractItemData(recentlyAddedItems, queryTypeSpecifics)
    (plainMessage, htmlMessage) = generateHtml(newItemList, queryTypeSpecifics)
    log.debug(
        f'[RETURN] jellyfin/main : \nPLAIN:\n{plainMessage} \nHTML:\n{htmlMessage}')
    return (plainMessage, htmlMessage)
