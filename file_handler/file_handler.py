"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import colorama
import json
import os
import re
import shutil
import subprocess
import urllib.request as rq

from generic_app.generic_app import GenericApp


class FileHandler:

    def __init__(self, app: GenericApp):
        self.__app = app
        self.__staging = os.path.join(app.target_dir, f".staging-{app.random_id}")
        self.__old_version = os.path.join(app.target_dir, f".oldver-{app.random_id}")

    def __project_download(self):
        try:
            os.mkdir(self.__staging)
        except FileExistsError:
            shutil.rmtree(self.__staging)
            os.mkdir(self.__staging)
        releases_latest = self.__app.version_latest
        if not isinstance(releases_latest, list):
            my_list = [releases_latest]
            releases_latest = my_list
        if len(releases_latest) == 0:
            print("No matching downloads for the latest version")
            raise ValueError
        for release in releases_latest:
            url = release['blob']
            print(f"Trying to get file from: {url}")
            download = rq.urlretrieve(url, os.path.join(self.__app.target_dir, self.__staging))
            filename = os.path.split(download)[-1]
            if re.fullmatch("^.*\\.(zip|rar|xz|7z)$", filename):
                subprocess.run(f"7z x -aoa {filename}", cwd=self.__staging, stdout=subprocess.DEVNULL)
                os.remove(os.path.join(self.__staging, filename))
            elif re.fullmatch("^.*\\.exe$", filename):
                os.rename(os.path.join(self.__staging, filename),
                          os.path.join(self.__staging, f"{self.__app.name}.exe"))

    def __project_normalize(self):
        dirs_normalized = False
        while not dirs_normalized:
            extracted = os.listdir(self.__staging)
            if len(extracted) == 0:
                print("Failure listing directory")
                raise FileNotFoundError
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
                    dirs_normalized = True
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
                dirs_normalized = True
        with open(os.path.join(self.__staging, "superelixier.json"), "w") as file:
            json.dump(self.__app.version_latest, file)

    def __project_merge_oldnew(self):
        for appdata in self.__app.appdatas:
            old_location = os.path.join(self.__old_version, appdata)
            new_location = os.path.join(self.__app.appdir, appdata)
            if os.path.exists(old_location):
                if os.path.isfile(old_location):
                    os.replace(old_location, new_location)
                elif os.path.isdir(old_location):
                    os.rename(old_location, new_location)
            else:
                print(colorama.Fore.MAGENTA + f"Old {appdata} not found.")

    def __create_target_dir(self):
        try:
            os.mkdir(self.__app.target_dir)
        except FileExistsError:
            pass

    def project_update(self):
        self.__create_target_dir()
        self.__project_download()
        self.__project_normalize()
        os.rename(self.__app.appdir, self.__old_version)
        os.rename(self.__staging, self.__app.appdir)
        self.__project_merge_oldnew()
        shutil.rmtree(os.path.join(self.__app.target_dir, self.__old_version))

    def project_install(self):
        self.__create_target_dir()
        self.__project_download()
        self.__project_normalize()
        os.rename(self.__staging, self.__app.appdir)
