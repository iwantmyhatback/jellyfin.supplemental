from connection import jellyfinConnection
from operator import itemgetter
from utilities import isAquiredThisWeek, stringToDate, replaceEveryNth, generateHeader
from json import load as loadJson
from requests import get as httpGET

info = loadJson(open("info.json"))


def main():
    client = jellyfinConnection()

    recentlyAddedMovies = client.jellyfin.get_recently_added(
        limit=1000, media='movie')

    newMovieList = []
    baseApiUrl = "https://api.themoviedb.org/3/movie/{movieId}/images?language=en&api_key={apiKey}"
    baseImageUrl = "http://image.tmdb.org/t/p/w185/{imageId}"
    baseYoutube = "https://www.youtube.com/watch?v={trailerId}"

    for movie in recentlyAddedMovies:
        addedDate = stringToDate(
            movie.get("DateCreated"), "%Y-%m-%dT%H:%M:%S.%f")
        if isAquiredThisWeek(addedDate):
            # Parse Movie Title
            movieTitle = movie.get("Name")

            # Parse Movie Overview
            movieOverview = movie.get("Overview")

            # Parse Tag List
            movieTagList = ', '.join(movie.get("Tags"))

            # Parse Genre List
            movieGenreList = ', '.join(movie.get("Genres"))

            # Parse Movie Poster URL
            movieId = movie.get("ProviderIds").get('Tmdb')
            tmdbApiKey = info.get('TMDB').get('API_KEY')
            response = httpGET(url=baseApiUrl.format(
                movieId=movieId, apiKey=tmdbApiKey))
            responseDict = response.json()

            if responseDict.get('success') == False:
                print(
                    f'[WARN] TMDB Connection Error : Movies Request for {movieTitle}\nJSON : {responseDict}')
                continue

            imageFile = responseDict.get('posters')[0].get('file_path')
            moviePosterUrl = baseImageUrl.format(imageId=imageFile)

            # Parse Movie Release Year
            if movie.get("PremiereDate"):
                moviePremierDate = stringToDate(
                    movie.get("PremiereDate"), "%Y-%m-%dT%H:%M:%S.%f")
                movieYear = moviePremierDate.year
            else:
                moviePremierDate = 'Unknown'

            # Parse Content Rating
            if movie.get("OfficialRating"):
                movieContentRating = movie.get("OfficialRating")
            else:
                movieContentRating = 'Unknown'

            # Parse Critic Rating
            if movie.get("CriticRating"):
                movieCriticRating = "Critics: {}% ".format(
                    movie.get("CriticRating"))
            else:
                movieCriticRating = ''

            # Parse Community Rating
            if movie.get("CommunityRating"):
                withCritic = '& ' if movieCriticRating != '' else ''
                roundedRating = round(float(movie.get("CommunityRating")), 1)
                movieCommunityRating = "Community: {}/10 {}".format(
                    roundedRating, withCritic)
            else:
                movieCommunityRating = ''

            # Parse Trailer URL
            if len(movie.get("RemoteTrailers")) > 0:
                trailerItem = movie.get("RemoteTrailers")[0]
                trailerUrl = trailerItem.get('Url')
                movieTrailerUrl = None

                if 'watch?v=' in trailerUrl:
                    trailerId = trailerUrl.rsplit('watch?v=', 1)[-1]
                elif 'video_id=' in trailerUrl:
                    trailerId = trailerUrl.rsplit('video_id=', 1)[-1]

                if trailerId is not None:
                    movieTrailerUrl = baseYoutube.format(trailerId=trailerId)
            else:
                movieTrailerUrl = None

            newMovieList.append(
                {
                    "title": movieTitle,
                    "overview": replaceEveryNth(movieOverview, " ", " \n", 15),
                    "tags": movieTagList,
                    "genres": movieGenreList,
                    "image": moviePosterUrl,
                    "year": movieYear,
                    "content": movieContentRating,
                    "critic": movieCriticRating,
                    "community": movieCommunityRating,
                    "trailer": movieTrailerUrl,
                }
            )

    newMovieList = sorted(newMovieList, key=itemgetter("year"), reverse=True)

    (plainMessage, htmlMessage) = generateHeader("Movie(s)", len(newMovieList))

    for movie in newMovieList:
        plainMessage += f"""
            {movie.get('title')}\n
            Content Rating: {movie.get('content')}\n
            {movie.get('community')}
            {movie.get('critic')}\n
            Year: {movie.get('year')}\n
            Tags: {movie.get('tags')}\n
            Genres: {movie.get('genres')}\n
            Summary: {movie.get('overview')}\n
            Trailer: {movie.get('trailer')}\n\n
        """
        htmlMessage += (
            f'<div style="display: flex;">'
            f'<div style="flex: 1;margin: 5% 2% 5% 2%;">'
            f"<img style=\"width:25vw;\" src=\"{movie.get('image')}\" />"
            f"</div>"
            f'<div style="flex: 5;margin: 8% 2% 8% 2%;">'
            f"<b style=\"font-size:1.5em;\">{movie.get('title')}</b>"
            f"<br>"
            f"<b>Year: </b><span>{movie.get('year')}</span>"
            f"<br>"
            f"<b>Content Rating: </b><span>{movie.get('content')}</span>"
            f"<br>"
            f"<b>Quality Ratings: </b><span>{movie.get('community')}</span><span>{movie.get('critic')}</span>"
            f"<br>"
            f"<b>Tags: </b><span>{movie.get('tags')}</span>"
            f"<br>"
            f"<b>Genres: </b><span>{movie.get('genres')}</span>"
            f"<br>"
            f"<b>Summary: </b><span>{movie.get('overview')}</span>"
            f"<br><br>"
            f"<a href=\"{movie.get('trailer')}\">Trailer</a>"
            f"<br>"
            f"</div>"
            f"<br>"
            f"</div>"
            f"<br>"
        )

    return (plainMessage, htmlMessage)
