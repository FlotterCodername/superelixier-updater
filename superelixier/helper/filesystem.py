"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os

DIR_APP: str = os.path.normpath(os.path.join(__file__, "..", "..", ".."))
DIR_CFG: str = os.path.join(DIR_APP, "config")


def remove_empty_dirs(top_dir: str, delete_top=False) -> None:
    """
    Delete empty folders created by this program. Do not use on app folders! We don't mess with the UX of installed
    apps that way.

    :param top_dir:
    :param delete_top:
    """
    empty_dirs = True
    while empty_dirs:
        empty_dirs = False
        for root, subdirs, _ in os.walk(top_dir):
            for subdir in subdirs:
                my_path = os.path.join(root, subdir)
                if len(os.listdir(os.path.join(root, subdir))) == 0:
                    empty_dirs = True
                    os.rmdir(my_path)
    if delete_top:
        try:
            if len(os.listdir(top_dir)) == 0:
                os.rmdir(top_dir)
        except FileNotFoundError:
            pass


def make_path_native(path: str) -> str:
    crumbs = path.split("/")
    if ":" in crumbs[0] and ":\\" not in crumbs[0]:
        crumbs[0] = crumbs[0].replace(":", ":\\")
    return os.path.join(*crumbs)


def simple_folder_list(folder):
    """

    :param folder: Folder to scan
    :return: List of absolute file paths
    """
    full_list = []
    for root, _, files in os.walk(folder):
        for file in files:
            my_path = os.path.join(root, file)
            if os.path.isfile(my_path):
                full_list.append(my_path)
    return full_list
