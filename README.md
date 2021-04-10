# Superelixier Updater
Superelixier Updater can automatically update a number of apps provided in portable form.
It can easily be extended to more programs by a user that has a basic knowledge of JavaScript Object Notation (JSON) and regular expressions.
Currently, it handles apps distributed on GitHub. 

![Example console output of this program](/docs/example.png)

## Features
- No unnecessary downloads: Checks the installed app for update and only downloads releases if there is a new one. Let's not waste bandwidth.
- Extensible: Adding more apps requires only basic knowledge of JSON and regular expressions.
    - Release files detected via regular expression.
    - Can specify files that should be deleted from release (for files you do not need)
    - Can specify any files or folders that hold configuration data or similar. These carry over to the new version.

## Usage
Superelixier Updater is in a very early stage of development. The first-time setup is not friendly to non-technical users yet. If you haven't used Python before, read closely. **On the bright side**: once set up, using this tool is as simple as running the ``main.py`` file with Python.

### First-time setup
- This tool requires a Python 3 interpreter. I personally use the latest version of [PyPy](https://www.pypy.org/), but you can also install versions >=3.7 of [standard Python](https://www.python.org/).
- Download or clone this repository.
- Three configuration files in the ``config`` folder need to be set up.
  - ``available.json`` is included. This holds patterns that the tool needs to detect, download and install updates.
    - Please check the ``blob_unwanted`` parameters: If you don't want to delete anything from the downloaded update, the lines should look like this: ``"blob_unwanted": [],``. Nevertheless, I have pre-set some parameters as configuration examples.
    - **IMPORTANT!** If nothing is set in ``appdatas``, *all* files from the old version will be deleted. This ensures that your app folder is clean. Anything that you want to keep from the old version needs to be in the ``appdatas`` parameter, e.g.:
    ```json
      "appdatas": [
        "configuration_folder",
        "config.ini",
        "other_configuration_file.cfg",
        "other_configuration_folder"
      ]
    ``` 
  - ``auth.json`` holds credentials needed to connect to sites hosting downloads. Simply rename the provided ``auth_example.json`` to ``auth.json``. The only credential you can set is a GitHub personal access token. You won't need this unless you run the updater compulsively. 
  - ``local.json`` tells the tool where to install which app. Rename the ``local_example.json`` to ``local.json`` and set your options.
  
### Running the updater
- **REMINDER: This software is provided as-is without absolutely any warranty. Use this at your own risk.**
  - This reminder is necessary as an incorrect configuration could lead to loss of data. But if the program were to crash, you'll have your previous files in a folder ``oldver-{random_id}`` that sits next to the app's directory.
- If your configuration is set up, you can now double-click the ``main.py`` file to run the updater with Python.

## Planned
- Running detection: Skip apps that have opened files
- Patterns: Replace user-facing regular expressions with a simpler wildcard system
- GitHub: Allow user to download pre-release versions or not
- HTML: Parser
- Appveyor: Crawler
- Buildbot: Crawler
- GUI:
  - Present update progress 
  - Configuration editing
