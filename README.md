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
  - ``available.json`` is included. This holds patterns that the tool needs to detect, download and install updates. Please check the 'blob_unwanted' parameters: If you don't want to delete anything from the downloaded update, the lines should look like this: ``"blob_unwanted": [],``. Nevertheless, I have pre-set some parameters as configuration examples. 
  - ``auth.json`` holds credentials needed to connect to sites hosting downloads. Simply rename the provided ``auth_example.json`` to ``auth.json``. The only credential you can set is a GitHub personal access token. You won't need this unless you run the updater a ridiculous amount of times. 
  - ``local.json`` tells the tool where to install which app. Rename the ``local_example.json`` to ``local.json`` and set your desired options.
  
## Planned
- Patterns: Replace user-facing regular expressions with a simpler wildcard system
- GitHub: Allow user to download pre-release version or not
- HTML: Parser
- Appveyor: Crawler
- Buildbot: Crawler
- GUI:
  - Present update progress 
  - Configuration editing
