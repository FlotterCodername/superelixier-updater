# Adding Apps

The JSON files in ``/definitions`` hold patterns that the tool needs to detect, download and install updates. The JSON file's name is not relevant to functionality, but we're using all-lowercase file names for uniformity.

## Basic parameters

*Documentation forthcoming*

## Unwanted files

If you want to delete something from a downloaded app, e.g. a ``vcredist`` setup that you already have installed anyway,
set up the  ``blob_unwanted`` parameter. This parameter takes regular expressions. Example:

````json
"blob_unwanted": [
"vc_redist.x64\\.exe",
"^app.*source.*\\.(zip|rar|xz|7z)$"
],
````

The first entry deletes an installation package with the filename ``vc_redist.x64.exe``. The backslashes are necessary
because ``.`` is a special character in regular expressions. It's a double backslash because ``\`` is a special
character in JSON strings.

The second entry is a more elaborate regular expression that deletes a hypothetical source code archive. To learn more
about regular expressions, check out [this w3schools article](https://www.w3schools.com/python/python_regex.asp).

If you don't want to delete anything from the downloaded update, the line should look like
this: ``"blob_unwanted": [],``

## Appdata

If nothing is set in ``appdatas``, *all* files could potentially be replaced by updates, if they came with the update.
If that happens, there are backups: All old files are retained in ``<app directory>/.superelixier_history/<date>T<time>``
.

Usually though, developers do not ship such files with their updates. You can still protect files from being overwritten
using the ``appdatas`` parameter, like so:

  ```json
"appdatas": [
"configuration_folder",
"config.ini",
"other_configuration_file.cfg",
"other_configuration_folder",
"folder_where_i_want_to_keep_only/this_file.ini"
]
  ``` 

Note that in ``folder_where_i_want_to_keep_only``, only ``this_file.ini`` will be protected. Also, regular expressions
are not supported here.
