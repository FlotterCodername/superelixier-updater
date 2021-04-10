# Superelixier Updater
Superelixier Updater can automatically update a number of apps provided in portable form.
It can easily be extended to more programs by a user that has a basic knowledge of JavaScript Object Notation (JSON) and regular expressions.
Currently, it handles apps distributed on GitHub. 

## Features
- No unnecessary downloads: Checks the installed app for update and only downloads releases if there is a new one.
- Extensible: Adding more apps requires only basic knowledge of JSON and regular expressions.
    - Release files detected via regular expression.
    - Can specify files that should be deleted from release (for files you do not need)
    - Can specify any files or folders that hold configuration data or similar. These will be kept from the old version.

## Planned
- Patterns: Replace user-facing regular expressions with a simpler wildcard system
- GitHub: Allow user to download pre-release version or not
- HTML: Parser
- Appveyor: Crawler
- Buildbot: Crawler
- GUI:
  - Present update progress 
  - Configuration editing
