from connection import jellyfinConnection
from operator import itemgetter
from utilities import isAquiredThisWeek, stringToDate, replaceEveryNth, generateHeader
from json import load as loadJson
from requests import get as httpGET

info = loadJson(open("info.json"))


def main():
    client = jellyfinConnection()

    try:
        recentlyAddedSeries = client.jellyfin.user_items(
            handler="/Latest",
            params={
                'fields': ['DateCreated', 'DateLastMediaAdded', 'Tags', 'Genres', 'ProviderIds', 'RemoteTrailers', 'Overview'],
                'includeItemTypes': ['Series'],
                'limit': 1000
            }
        )
    except:
        print('[ERROR] There was an error getting latest episodes')
        exit()

    newSeriesList = []
    baseApiUrl = "https://api.themoviedb.org/3/tv/{seriesId}/images?language=en&api_key={apiKey}"
    baseImageUrl = "http://image.tmdb.org/t/p/w185/{imageId}"
    baseYoutube = "https://www.youtube.com/watch?v={trailerId}"

    for series in recentlyAddedSeries:
        addedDate = stringToDate(
            series.get("DateLastMediaAdded"), "%Y-%m-%dT%H:%M:%S.%f")

        if isAquiredThisWeek(addedDate):
            # Parse Movie Title
            seriesTitle = series.get("Name")

            # Parse Movie Overview
            seriesOverview = series.get("Overview")

            # Parse Tag List
            seriesTagList = ', '.join(series.get("Tags"))

            # Parse Genre List
            seriesGenreList = ', '.join(series.get("Genres"))

            # Parse Movie Poster URL
            seriesId = series.get("ProviderIds").get('Tmdb')
            tmdbApiKey = info.get('TMDB').get('API_KEY')
            response = httpGET(url=baseApiUrl.format(
                seriesId=seriesId, apiKey=tmdbApiKey))
            responseDict = response.json()

            if responseDict.get('success') == False or len(responseDict.get('posters')) < 1:
                print(
                    f'[WARN] TMDB Connection Error : Series Request for {seriesTitle}\nJSON : {responseDict}')
                continue

            imageFile = responseDict.get('posters')[0].get('file_path')
            seriesPosterUrl = baseImageUrl.format(imageId=imageFile)

            # Parse Movie Release Year
            if series.get("PremiereDate"):
                seriesPremierDate = stringToDate(
                    series.get("PremiereDate"), "%Y-%m-%dT%H:%M:%S.%f")
                seriesYear = seriesPremierDate.year
            else:
                seriesYear = 0000

            # Parse Content Rating
            if series.get("OfficialRating"):
                seriesContentRating = series.get("OfficialRating")
            else:
                seriesContentRating = 'Unknown'

            # Parse Critic Rating
            if series.get("CriticRating"):
                seriesCriticRating = "Critics: {}% ".format(
                    series.get("CriticRating"))
            else:
                seriesCriticRating = ''

            # Parse Community Rating
            if series.get("CommunityRating"):
                withCritic = '& ' if seriesCriticRating != '' else ''
                roundedRating = round(float(series.get("CommunityRating")), 1)
                seriesCommunityRating = "Community: {}/10 {}".format(
                    roundedRating, withCritic)
            else:
                seriesCommunityRating = ''

            # Parse Trailer URL
            if len(series.get("RemoteTrailers")) > 0:
                trailerItem = series.get("RemoteTrailers")[0]
                trailerUrl = trailerItem.get('Url')
                seriesTrailerUrl = None

                if 'watch?v=' in trailerUrl:
                    trailerId = trailerUrl.rsplit('watch?v=', 1)[-1]
                elif 'video_id=' in trailerUrl:
                    trailerId = trailerUrl.rsplit('video_id=', 1)[-1]

                if trailerId is not None:
                    seriesTrailerUrl = baseYoutube.format(trailerId=trailerId)
            else:
                seriesTrailerUrl = None

            newSeriesList.append(
                {
                    "title": seriesTitle,
                    "overview": replaceEveryNth(seriesOverview, " ", " \n", 15),
                    "tags": seriesTagList,
                    "genres": seriesGenreList,
                    "image": seriesPosterUrl,
                    "year": seriesYear,
                    "content": seriesContentRating,
                    "critic": seriesCriticRating,
                    "community": seriesCommunityRating,
                    "trailer": seriesTrailerUrl,
                }
            )

    newSeriesList = sorted(newSeriesList, key=itemgetter(
        "year"), reverse=True)

    (plainMessage, htmlMessage) = generateHeader(
        "Series(s)", len(newSeriesList))

    for series in newSeriesList:
        plainMessage += f"""
            {series.get('title')}\n
            Content Rating: {series.get('content')}\n
            {series.get('community')}
            {series.get('critic')}\n
            Year: {series.get('year')}\n
            Tags: {series.get('tags')}\n
            Genres: {series.get('genres')}\n
            Summary: {series.get('overview')}\n
            Trailer: {series.get('trailer')}\n\n
        """
        htmlMessage += (
            f'<div style="display: flex;">'
            f'<div style="flex: 1;margin: 5% 2% 5% 2%;">'
            f"<img style=\"width:25vw;\" src=\"{series.get('image')}\" />"
            f"</div>"
            f'<div style="flex: 5;margin: 8% 2% 8% 2%;">'
            f"<b style=\"font-size:1.5em;\">{series.get('title')}</b>"
            f"<br>"
            f"<b>Year: </b><span>{series.get('year')}</span>"
            f"<br>"
            f"<b>Content Rating: </b><span>{series.get('content')}</span>"
            f"<br>"
            f"<b>Quality Ratings: </b><span>{series.get('community')}</span><span>{series.get('critic')}</span>"
            f"<br>"
            f"<b>Tags: </b><span>{series.get('tags')}</span>"
            f"<br>"
            f"<b>Genres: </b><span>{series.get('genres')}</span>"
            f"<br>"
            f"<b>Summary: </b><span>{series.get('overview')}</span>"
            f"<br><br>"
            f"<a href=\"{series.get('trailer')}\">Trailer</a>"
            f"<br>"
            f"</div>"
            f"<br>"
            f"</div>"
            f"<br>"
        )

    return (plainMessage, htmlMessage)
