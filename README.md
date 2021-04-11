# Superelixier Updater
**Operating this tool currently requires some technical knowledge about JavaScript Object Notation (JSON) and regular expressions.
As development progresses, this will change.**
If you want to wait for a user-friendly version, select ``Watch -> Custom -> Releases`` from the top of this GitHub repository.

Superelixier Updater can automatically update a number of apps provided in portable form.
It can easily be extended to more programs by a technical user. Currently, it handles apps distributed on GitHub and HTML pages. 

![Example console output of this program](/docs/example.png)

## Features
- No unnecessary downloads: Checks the installed app for update and only downloads releases if there is a new one. Let's not waste bandwidth.
- Extensible: Add more apps via configuration files.
    - Release files detected via regular expression.
    - Can specify files that should be deleted from release (for files you do not need)
    - Can specify any files or folders that hold configuration data or similar. These carry over to the new version.

## Usage
The first-time setup is not friendly to non-technical users yet. If you haven't used Python before, read closely. **On the bright side**: once set up, using this tool is as simple as running the ``main.py`` file with Python.

### Requirements
- Python 3 interpreter. I use the latest version of [PyPy](https://www.pypy.org/), but you can also install versions >=3.7 of [standard Python](https://www.python.org/).
- [Use pip to install](https://packaging.python.org/tutorials/installing-packages/#use-pip-for-installing) the packages ``colorama`` and ``requests``.
- 7z is used to extract archives and must be in PATH.

### First-time setup
- Download or clone this repository.
- Three configuration files in the ``config`` folder need to be set up.
  - ``available.json`` is included. This holds patterns that the tool needs to detect, download and install updates.
    Please check the ``blob_unwanted`` parameters: If you don't want to delete anything from the downloaded update, the lines should look like this: ``"blob_unwanted": [],``. Nevertheless, I have pre-set some parameters as configuration examples.
    **IMPORTANT:** If nothing is set in ``appdatas``, *all* files from the old version will be deleted. This ensures that your app folder is clean. Anything that you want to keep from the old version needs to be in the ``appdatas`` parameter, like so:
    ```json
      "appdatas": [
        "configuration_folder",
        "config.ini",
        "other_configuration_file.cfg",
        "other_configuration_folder",
        "folder_where_i_want_to_keep_only/this_file.ini"
      ]
    ``` 
    Note that in ``folder_where_i_want_to_keep_only``, only ``this_file.ini`` will be retained.
  - ``auth.json`` holds credentials needed to connect to sites hosting downloads. Simply rename the provided ``auth_example.json`` to ``auth.json``. The only credential you can set is a GitHub personal access token. You won't need this unless you run the updater compulsively. 
  - ``local.json`` tells the tool where to install which app. Rename the ``local_example.json`` to ``local.json`` and set your options.
  
### Running the updater
- **REMINDER: This software is provided as-is without absolutely any warranty. Use this at your own risk.**
  - This reminder is necessary because an incorrect configuration could lead to loss of data. In case the program crashes, you'll have your previous files in a folder ``oldver-{random_id}`` that sits next to the app's directory. I'm still working on a scheme that lets the user keep a number of old versions.
- If your configuration is set up, you can now double-click the ``main.py`` file to run the updater with Python.

## Planned
- Running detection: Skip apps that have opened files
- Patterns: Replace user-facing regular expressions with a simpler wildcard system
- GitHub: Allow user to download pre-release versions or not
- Appveyor: Crawler
- Buildbot: Crawler
- GUI:
  - Present update progress 
  - Configuration editing
