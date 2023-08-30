# jellyfin.supplemental

This is a small script set which leverages a few external resources to gather media information and send an email which describes the Movies and Shows which have been updated in the Hellyfin instance within the past 7 days. There are a few prerequisites to running this script:<br>

- An existing [Jellyfin](https://jellyfin.org) setup holding personal media collection
- A [Google developer account](http://console.developers.google.com) for leveraging the Gmail API to send an email
- A [TMDB developer account](https://developer.themoviedb.org) for leveraging the TMDB API to use external poster images for the email HTML

Though designed to run through a Docker container using the entry script `<repoRoot>/shell/runRoutine.sh` it can also be run locally without a Docker container using `<repoRoot>/shell/main.sh`.

The scripting should is POSIX compliant (usable with most modern shells), and the python code uses Python3 (tested with 3.11.4)

See README's for:<br>
[credentials](.credentials/README.md)<br>
[configuration](configuration/README.md)<br>
[python](python/README.md)<br>
[shell](shell/README.md)<br>
