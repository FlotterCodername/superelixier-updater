# Superelixier Updater

[![Python app](https://github.com/FlotterCodername/superelixier-updater/actions/workflows/python-app.yml/badge.svg)](https://github.com/FlotterCodername/superelixier-updater/actions/workflows/python-app.yml) [![CodeQL](https://github.com/FlotterCodername/superelixier-updater/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/FlotterCodername/superelixier-updater/actions/workflows/codeql-analysis.yml)

**Using this tool currently requires basic knowledge about JavaScript Object Notation (JSON). As development progresses,
this will change.** If you want to wait for a user-friendly version, select ``Watch -> Custom -> Releases`` from the top
of the GitHub repository. In any case, check out the [list of Pre-configured Apps](./docs/Available%20Apps.md)

Users who add additional apps definitions to the updater need to be familiar with JSON and regular expressions.

Superelixier Updater can automatically update a number of apps provided in portable form. Currently, it handles apps
distributed on Appveyor, GitHub and HTML pages.

![Example console output of this program](./docs/example.png)

## Usage

The first-time setup is not friendly to non-technical users yet. **On the bright side**: once set up, using this tool is
as simple as running the ``superelixier.exe`` file.

### Requirements

- Windows 10+ 64-Bit

### First-time setup

- Download and extract the latest preview release.
- Two configuration files in the ``config`` folder need to be set up.
    - ``auth.json`` will be auto-created if it's missing. Most users don't need to change anything here, as modest
      amounts of API calls can be done without authentification tokens.
    - ``local.json`` tells the tool where to install which app. Rename the ``local_example.json`` to ``local.json`` and
      set your options. Make sure you use forward slashes in your paths.

### Running the updater

- **REMINDER: This software is provided as-is without absolutely any warranty. Use this at your own risk.**
    - This reminder is necessary because a bad configuration could lead to unexpected behavior. In case anything goes
      wrong, you'll have your previous files in a folder ``.superelixier-history`` that sits in the app's directory. As
      of now, the updater doesn't delete any of your old files at all: everything goes into the history folder instead.
- If your configuration is set up, you run the ``superelixier.exe`` file to run the updater.

## Features

- No unnecessary downloads: Checks the installed app for update and only downloads releases if there is a new one. Let's
  not waste bandwidth (caveat: only detects updates it did itself).
- Running detection: Downloaded updates will be applied next run if the folder was in use this run.
- Extensible: Add more apps via configuration files.
    - Release files detected via regular expression.
    - Can specify files that should be deleted from release (for files you do not need)
    - Can specify any files or folders that should be protected from being replaced by updates.


## Planned
Planned features are tracked via [labeled GitHub Issues](https://github.com/FlotterCodername/superelixier-updater/issues?q=is%3Aopen+is%3Aissue+label%3Aaccepted+label%3Aepic%2Cenhancement).
