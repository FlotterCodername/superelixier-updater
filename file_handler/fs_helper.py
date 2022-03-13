import os
import re

from generic_app.generic_app import GenericApp
from helper.terminal import MAGENTA


def remove_empty_dirs(top_dir: str, delete_top=False) -> None:
    """
    Delete empty folders created by this program. Do not use on app folders! We don't mess with the UX of installed
    apps that way.

    :param top_dir:
    :param delete_top:
    :return:
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


def list_appdatas(app: GenericApp):
    keep_list = []
    missing_appdata = []
    for appdata in app.appdatas:
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
        print(MAGENTA + "Old appdatas not found: %s" % ", ".join(missing_appdata))
    return keep_list


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
        print(MAGENTA + f"{app.name}: Folder is in use. Update files will be moved next time.")
        for key in opened_files:
            opened_files[key].close()
        return None
    except OSError:
        print(MAGENTA + f"{app.name}: Couldn't get folder lock.")
        for key in opened_files:
            opened_files[key].close()
        return None
    return opened_files
