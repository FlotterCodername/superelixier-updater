"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import cgi

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
        # Create folder structure if it doesn't exist
        os.makedirs(self.__staging, exist_ok=True)
        # Make sure staging directory is empty
        shutil.rmtree(self.__staging)
        os.mkdir(self.__staging)
        release_latest = self.__app.version_latest["blobs"]
        if len(release_latest) == 0:
            print("No matching downloads for the latest version")
            raise ValueError
        for url in release_latest:
            print(f"Trying to get file from: {url}")
            cgi_file_filename = rq.urlopen(url).info()['Content-Disposition']
            if cgi_file_filename is None:
                filename = url.split("/")[-1]
            else:
                value, params = cgi.parse_header(cgi_file_filename)
                filename = params["filename"]
            download = rq.urlretrieve(url, os.path.join(self.__app.target_dir, self.__staging, filename))
            filename = os.path.split(download[0])[-1]
            if re.fullmatch("^.*\\.(001|7z|bz2|bzip2|gz|gzip|lzma|rar|tar|tgz|txz|xz|zip)$", filename):
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
        # Data to keep
        keep_list = []
        missing_appdata = []
        for appdata in self.__app.appdatas:
            data = os.path.join(self.__old_version, *appdata.split("/"))
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
        # Full dir tree list
        full_list = []
        for root, _, files in os.walk(self.__old_version):
            for file in files:
                my_path = os.path.join(root, file)
                if os.path.isfile(my_path):
                    full_list.append(my_path)
        # Remove files to keep from list before purging
        for file in keep_list:
            if file in full_list:
                full_list.remove(file)
        # Purge files
        for file in full_list:
            os.remove(file)
        # Move to new location
        for keep_file in keep_list:
            old_location = keep_file
            new_location = keep_file.replace(self.__old_version, self.__app.appdir)
            os.makedirs(os.path.split(new_location)[0], exist_ok=True)
            if os.path.exists(new_location):
                os.replace(old_location, new_location)
            else:
                os.rename(old_location, new_location)
        # Purge empty dirs. This leaves an empty directory if all went well.
        # If it's not empty, project_update() will raise an error.
        self.__remove_empty_dirs(self.__old_version)

    @staticmethod
    def __remove_empty_dirs(top_dir):
        empty_dirs = True
        while empty_dirs:
            empty_dirs = False
            for root, subdirs, _ in os.walk(top_dir):
                for subdir in subdirs:
                    my_path = os.path.join(root, subdir)
                    if len(os.listdir(os.path.join(root, subdir))) == 0:
                        empty_dirs = True
                        os.rmdir(my_path)

    def project_update(self):
        self.__project_download()
        self.__project_normalize()
        os.rename(self.__app.appdir, self.__old_version)
        os.rename(self.__staging, self.__app.appdir)
        self.__project_merge_oldnew()
        os.rmdir(os.path.join(self.__app.target_dir, self.__old_version))

    def project_install(self):
        self.__project_download()
        self.__project_normalize()
        os.rename(self.__staging, self.__app.appdir)
