# Adding Apps

``available.json`` holds patterns that the tool needs to detect, download and install updates.

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

**IMPORTANT:** If nothing is set in ``appdatas``, *all* files from the old version will be deleted. This ensures that
your app folder is clean. Anything that you want to keep from the old version needs to be in the ``appdatas`` parameter,
like so:

  ```json
"appdatas": [
"configuration_folder",
"config.ini",
"other_configuration_file.cfg",
"other_configuration_folder",
"folder_where_i_want_to_keep_only/this_file.ini"
]
  ``` 

Note that in ``folder_where_i_want_to_keep_only``, only ``this_file.ini`` will be retained. Also, regular expressions
are not supported here.