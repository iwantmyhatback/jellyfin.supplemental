# jellyfin.supplemental/python

The Python content for this script set

## connection.py

Uses configuration files from `<repoRoot>/configuration/info*.json` to connect to Jellyfin and return a client

## gmail.py

Uses configuration files from `<repoRoot>/configuration/info*.json` to connect to Gmail and use the API to send an Email

## htmlProcessing.py

Processes the compiled information in jellyfin.py into HTML for th email body

## jellyfin.py

Queries information from Jellyfin and processes the data to prepare it for HTML generation

## main.py

Performs the actions laid out in all the other Python files

## utilities.py
