"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import colorama
import datetime
import json
import os
import re
import requests
import shutil
import subprocess
from generic_app.generic_app import GenericApp


class FileHandler:

    def __init__(self, app: GenericApp):
        now_string = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H.%M.%S")
        self.__app = app
        self.__staging = os.path.join(app.target_dir, f".staging-{app.random_id}")
        self.__keep_history = True
        self.__history = os.path.join(app.appdir, ".superelixier_history", now_string)

    def __project_download(self):
        # Create folder structure if it doesn't exist
        os.makedirs(self.__staging, exist_ok=True)
        # Make sure staging directory is empty
        shutil.rmtree(self.__staging)
        os.mkdir(self.__staging)
        release_latest = self.__app.version_latest["blobs"]
        if len(release_latest) == 0:
            print("No matching downloads for the latest version")
        for url in release_latest:
            print(f"Trying to get file from: {url}")
            headers = {'User-Agent': 'Superelixier Updater (Contact: @FroyoXSG on GitHub)'}
            response = requests.get(url, allow_redirects=True, headers=headers)
            filename = os.path.join(self.__staging, self.__get_remote_filename(url, response))
            with open(filename, "wb") as file:
                file.write(response.content)
            if filename and re.fullmatch("^.*\\.(001|7z|bz2|bzip2|gz|gzip|lzma|rar|tar|tgz|txz|xz|zip)$", filename):
                subprocess.run(f"7z x -aoa {filename}", cwd=self.__staging, stdout=subprocess.DEVNULL)
                os.remove(os.path.join(self.__staging, filename))
            elif filename and re.fullmatch("^.*\\.exe$", filename):
                os.rename(os.path.join(self.__staging, filename),
                          os.path.join(self.__staging, f"{self.__app.name}.exe"))

    def __project_normalize(self):
        normalize_failure = False
        normalize_done = False
        while not normalize_done:
            extracted = os.listdir(self.__staging)
            if len(extracted) == 0:
                print("Failure downloading or extracting this app")
                normalize_done = True
                normalize_failure = True
            elif len(extracted) == 1:
                extracted_dir = os.path.join(self.__staging, extracted[0])
                if os.path.isdir(extracted_dir):
                    for file in os.listdir(extracted_dir):
                        shutil.move(
                            os.path.join(extracted_dir, file),
                            os.path.join(self.__staging, file)
                        )
                    os.rmdir(extracted_dir)
                elif os.path.isfile:
                    normalize_done = True
            elif len(extracted) > 1:
                print(colorama.Style.BRIGHT + f"{self.__app.name}: extracted files")
                strs = []
                for extracted in extracted:
                    print_string = extracted
                    for pattern in self.__app.blob_unwanted:
                        if re.fullmatch(pattern, extracted):
                            print_string = colorama.Fore.RED + extracted + " (removed)" + colorama.Fore.RESET
                            os.remove(os.path.join(self.__staging, extracted))
                    strs.append(print_string)
                print(", ".join(strs))
                normalize_done = True
        if not normalize_failure:
            with open(os.path.join(self.__staging, "superelixier.json"), "w") as file:
                json.dump(self.__app.version_latest, file)

    def __project_merge_oldnew(self):
        # Data to keep
        keep_list = self.__list_appdatas(self.__app)
        # Full dir tree list
        full_list = self.__list_folder(self.__staging)
        # Remove appdatas from staging
        for file in keep_list:
            file_to_protect = file.replace(self.__app.appdir, self.__staging)
            if file_to_protect in full_list:
                try:
                    os.remove(file_to_protect)
                    full_list.remove(file_to_protect)
                except PermissionError:
                    raise PermissionError(f"Error updating {self.__app.name}: Permission denied for {file_to_protect}")
        # Create history folder
        if self.__keep_history:
            os.makedirs(self.__history, exist_ok=True)
        # Move to new location
        for update_file in full_list:
            stage_location = update_file
            new_location = update_file.replace(self.__staging, self.__app.appdir)
            os.makedirs(os.path.split(new_location)[0], exist_ok=True)
            if os.path.exists(new_location):
                if self.__keep_history:
                    history_location = new_location.replace(self.__app.appdir, self.__history)
                    os.makedirs(os.path.split(history_location)[0], exist_ok=True)
                    os.rename(new_location, history_location)
                    os.rename(stage_location, new_location)
                else:
                    os.replace(stage_location, new_location)
            else:
                os.rename(stage_location, new_location)
        self.__remove_empty_dirs(self.__staging)
        # Ideally don't create these folders in the first place:
        self.__remove_empty_dirs(os.path.split(self.__history)[0], delete_top=True)

    @staticmethod
    def __list_folder(folder):
        full_list = []
        for root, _, files in os.walk(folder):
            for file in files:
                my_path = os.path.join(root, file)
                if os.path.isfile(my_path):
                    full_list.append(my_path)
        return full_list

    @staticmethod
    def __list_appdatas(app: GenericApp):
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
            print(colorama.Fore.MAGENTA + f"Old appdatas not found: {', '.join(missing_appdata)}")
        return keep_list

    @staticmethod
    def __remove_empty_dirs(top_dir, delete_top=False):
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
            if len(os.listdir(top_dir)) == 0:
                os.rmdir(top_dir)


    @staticmethod
    def __get_remote_filename(url, response):
        cd = response.headers.get('content-disposition')
        if not cd:
            filename = url.split("/")[-1]
        else:
            filename = re.findall('filename=(.+)', cd)[0]
        filename = filename.replace('"', '')
        return filename

    @staticmethod
    def make_path_native(path):
        crumbs = path.split("/")
        if ":" in crumbs[0] and ":\\" not in crumbs[0]:
            crumbs[0] = crumbs[0].replace(":", ":\\")
        return os.path.join(*crumbs)

    def project_update(self):
        self.__project_download()
        self.__project_normalize()
        self.__project_merge_oldnew()
        os.rmdir(self.__staging)

    def project_install(self):
        self.__project_download()
        self.__project_normalize()
        os.rename(self.__staging, self.__app.appdir)
