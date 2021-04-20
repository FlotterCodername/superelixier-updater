# Superelixier Updater

**Operating this tool currently requires some technical knowledge about JavaScript Object Notation (JSON) and regular
expressions. As development progresses, this will change.**
If you want to wait for a user-friendly version, select ``Watch -> Custom -> Releases`` from the top of this GitHub
repository.

Superelixier Updater can automatically update a number of apps provided in portable form. It can easily be extended to
more programs by a technical user. Currently, it handles apps distributed on Appveyor, GitHub and HTML pages.

![Example console output of this program](/docs/example.png)

## Features
- [List of Pre-configured Apps](Available%20Apps.md)
- No unnecessary downloads: Checks the installed app for update and only downloads releases if there is a new one. Let's
  not waste bandwidth.
- Extensible: Add more apps via configuration files.
    - Release files detected via regular expression.
    - Can specify files that should be deleted from release (for files you do not need)
    - Can specify any files or folders that should be protected from being replaced by updates.

## Usage

The first-time setup is not friendly to non-technical users yet. If you haven't used Python before, read closely. **On
the bright side**: once set up, using this tool is as simple as running the ``main.py`` file with Python.

### Requirements

- Python 3 interpreter. I use the latest version of [PyPy](https://www.pypy.org/), but you can also install version
  3.7 (or compatible) of [standard Python](https://www.python.org/).
- [Use pip to install](https://packaging.python.org/tutorials/installing-packages/#use-pip-for-installing) the
  packages ``colorama``, ``packaging`` and ``requests``.
- [7z](https://7-zip.org/7z.html) is used to extract archives and must be
  in [PATH](https://en.wikipedia.org/wiki/PATH_(variable)).

### First-time setup

- Download or clone this repository.
- Three configuration files in the ``config`` folder need to be set up.
    - ``available.json`` (included) holds patterns that the tool needs to detect, download and install updates. If
      you're not adding apps, there's normally nothing to do here. However, should files disappear from the app
      directory after an update (configuration files etc.), please read [Adding Apps](Adding%20Apps.md#Appdata) on what
      to do about it.
    - ``auth.json`` (included) holds credentials needed to connect to sites hosting downloads. Most users don't need to
      change anything here, as modest amounts of API calls can be done without tokens.
    - ``local.json`` tells the tool where to install which app. Rename the ``local_example.json`` to ``local.json`` and
      set your options. Make sure you use forward slashes in your paths.

### Running the updater

- **REMINDER: This software is provided as-is without absolutely any warranty. Use this at your own risk.**
    - This reminder is necessary because a bad configuration could lead to unexpected behavior. In case anything goes
      wrong, you'll have your previous files in a folder ``.superelixier_history`` that sits in the app's directory. As
      of now, the updater doesn't delete any of your old files at all: everything goes into the history folder instead.
- If your configuration is set up, you can now double-click the ``main.py`` file to run the updater with Python.

## Planned

- Running detection: Skip apps that have opened files
- History: Make number/age of kept backups configurable.
- Patterns: Replace user-facing regular expressions with a simpler wildcard system
- GitHub: Allow user to download pre-release versions or not
- Buildbot: Handler
- GUI:
    - Present update progress
    - Configuration editing
