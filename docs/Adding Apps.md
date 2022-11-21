# Adding Apps

The TOML files in ``/definitions`` hold patterns that the tool needs to detect, download and install updates. The TOML 
file's name is not relevant to functionality, but we're using all-lowercase file names for uniformity.

On start, this updater reads and validates the TOML files and makes them available to the program. So it is not
necessary to push them to the superelixier-updater repository before using them. BUT, in the spirit of collaboration,
please consider opening a Pull Request with any definitions you have written, so that all users may benefit. 

Knowledge of Python Regular Expressions (regex) is required.
[This w3schools article](https://www.w3schools.com/python/python_regex.asp) is highly recommended.

## Top sections
A valid definition has the following sections:
- ``info``
- ``appveyor``, ``github`` OR ``html``
- Optionally: ``local``

## Shared sections

Some sections in the definition are the same regardless of where an app is hosted.

### ``info`` section
This contains information that will be displayed in the updater and the documentation, mainly.

```toml
[info]
name = "My App Name"           # string, required. Use vendor's own stylization. Will be used to select this app
category = "Audio & Video"     # enum[...], optional. Further documentation below
gist = "Oneliner description"  # string, optional
```

### ``local`` section
This section describes how the updater should interact with the app's folder.  
```toml
[local]
appdata = "settings.ini"  # string or string[], optional. Further documentation below
delete = "Audio & Video"  # string or string[], optional. Further documentation below
installer = "sfx"         # enum["sfx", "innoextract"], optional. 
```
The most important parameter here is ``installer``:
- If the program is distributed as an archive or single ``.exe`` file, leave ``installer`` out
- If the program is distributed as "self-extracting archive", set ``installer = "sfx"``
- If the program is distributed as an InnoSetup installer, set ``installer = "innoextract"``

## ``appveyor`` section - AppVeyor apps
This is the least desired source for apps due to an API Key being all but required. New versions are identified by the
date of the build.
```toml
[appveyor]
blob_re = "^.*\\.exe$"  # string, required. Regex to run over the build artifact names
user = "developer"      # string, required. The user that owns the project
project = "appname"     # string, required. Which project to access from the user
branch = "main"         # string, optional. "master" will be assumed if not set
```

## ``github`` section - GitHub apps
This source gets apps from the "Releases" section on a GitHub project (GitHub Actions not yet supported).

This is the most desirable source for apps due to stability and ease of maintaining the definitions. New versions are
identified by the date of the release.
```toml
[github]
blob_re = "^.*\\.exe$"  # string, required. Regex to run over the release artifact names
user = "developer"      # string, required. The user that owns the project
project = "appname"     # string, required. Which project to access from the user
prerelease = true       # boolean, optional. Set true to allow releases that are tagged as pre-release
```

## ``html`` section - Web pages

This is a hacky way to get an app from any HTML page. New versions are identified by one of three ways, which must set
by the definition creator.

If the download link found here redirects to another host, the download of the app will fail. This is intentional and
meant as a safeguard mechanism.

There are two different methods to get an app from any HTML page:
- Permalink (**preferable**): If the latest version is always published at the same url, use this method.
- Variable link method (**danger zone**): If the latest version is not always published at the same url, use this method instead.
  This should not be used with untrusted pages. Any page with user input (such as comments) must be considered untrusted.

In either case, some parameters are shared:
```toml
[html]
url = "https://coolapp.org/downloads/"  # string, required. URL of the HTML page to parse
versioning = "tuple"                    # enum["id", "integer", "tuple"] how the app is versioned on the page
```
Versioning describes how to interpret version identifiers found on the page:
- ``versioning = "id"``: Update when a certain bit on the page changes (such as a commit ref or similar), e.g. ``9a5e7fb`` != ``94ca7f``
- ``versioning = "integer"``: Update when a newer download has a bigger number, e.g. ``9001`` > ``9000``
- ``versioning = "tuple"``: Update when the "dotted" version is higher, e.g. ``1.2.3`` > ``1.0.0``

### Permalink method (preferable)
```toml
[html]
url = ...
versioning = ...
# string, required. URL where the latest artifact will be published
blob_permalink = "https://coolapp.org/downloads/latest-portable.zip"
# string, required. regex with the version id as an unnamed group.
blob_permalink_re = "<span style=\".*?\">Cool App (.*?) latest portable ZIP</span>"
```

### Variable link method (danger zone)
```toml
[html]
url = ...
versioning = ...
# string, required. regex with group "url" for downloads and group "ver" for version IDs
blob_re = "<your regex here>"
```

## Detail information
### ``local.delete`` parameter
If you want to delete something from a downloaded app, e.g. a ``vcredist`` setup that most users already have installed
anyway, set up the ``delete`` parameter. This parameter uses regular expressions. Example:

```toml
delete = [
    "vc_redist.x64\\.exe",
    "^app.*source.*\\.(zip|rar|xz|7z)$",
]
```

The first entry deletes an installation package with the filename ``vc_redist.x64.exe``.
The second entry is a more elaborate regular expression that deletes a hypothetical source code archive.

### ``local.appdata`` parameter

If nothing is set in ``appdata``, *all* files could potentially be replaced by updates, if they came with the update.
If that happens, there are backups: All old files are retained in
``<app directory>/.superelixier_history/<date>T<time>``.

Usually though, developers do not ship such files with their updates. You can still protect files from being overwritten
using the ``appdata`` parameter, like so:

```toml
appdata = [
    "configuration_folder",
    "config.ini",
    "other_configuration_file.cfg",
    "other_configuration_folder",
    "folder_where_i_want_to_keep_only/this_file.ini",
]
``` 

Note that in ``folder_where_i_want_to_keep_only``, only ``this_file.ini`` will be protected. Also, regular expressions
are not supported here.
