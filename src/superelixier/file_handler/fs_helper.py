"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import re

from superelixier.generic.generic_app import GenericApp
from superelixier.helper.filesystem import simple_folder_list
from superelixier.helper.terminal import Ansi


def list_appdatas(app: GenericApp):
    keep_list = []
    missing_appdata = []
    for appdata in app.definition.local.appdata:
        data = os.path.join(app.appdir, *appdata.split("/"))
        if os.path.exists(data):
            if os.path.isfile(data):
                keep_list.append(data)
            if os.path.isdir(data):
                for root, _, files in os.walk(data):
                    for file in files:
                        my_file = os.path.join(root, file)
                        keep_list.append(my_file)
        else:
            missing_appdata.append(appdata)
    if len(missing_appdata) != 0:
        print(Ansi.MAGENTA + "Old appdatas not found: %s" % ", ".join(missing_appdata))
    return keep_list


def lock_folder(app, staging, staging_list):
    """
    Open all files in binary append mode to get exclusive access. Close all files if any file is in use.
    # TODO Make this a contextmanager
    :param staging_list:
    :param staging:
    :param app:
    :return: Dictionary with the file handles. Invoker must close these again.
    """
    opened_files = {}
    target_list = []
    for my_file in staging_list:
        target_list.append(my_file.replace(staging, app.appdir))
    # Here we could also check if any binaries are running and not even bother with trying to lock all files.
    file_list = simple_folder_list(app.appdir)
    for my_file in file_list:
        if my_file not in target_list:
            file_list.remove(my_file)
    try:
        for existing_file in file_list:
            # There is a limit of 2048 opened files per process.
            if len(file_list) <= 2000:
                if os.path.isfile(existing_file):
                    opened_files[existing_file] = open(existing_file, "ab")
            else:
                if os.path.isfile(existing_file) and re.search(
                    "\\.(bat|cmd|com|dll|exe|elf|js|jse|msc|ps1|sh|vbe|vbs|wsf|wsh)$",
                    os.path.split(existing_file)[-1].casefold(),
                ):
                    opened_files[existing_file] = open(existing_file, "ab")
    except PermissionError:
        print(f"{Ansi.MAGENTA}{app.name}: Folder is in use. Update files will be moved next time.")
        for key in opened_files:
            opened_files[key].close()
        return None
    except OSError:
        print(f"{Ansi.MAGENTA}{app.name}: Couldn't get folder lock.")
        for key in opened_files:
            opened_files[key].close()
        return None
    return opened_files
