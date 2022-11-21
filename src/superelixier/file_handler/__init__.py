"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import datetime
import json
import os
import re
import shutil
import subprocess

from superelixier.file_handler.downloader import Downloader
from superelixier.file_handler.fs_helper import list_appdatas, lock_folder
from superelixier.generic.generic_app import GenericApp, VersionInstalled
from superelixier.helper.environment import DIR_APP
from superelixier.helper.filesystem import remove_empty_dirs, simple_folder_list
from superelixier.helper.terminal import Ansi

BIN = os.path.join(DIR_APP, "bin-win32")
SEVENZIP = os.path.join(BIN, "7z.exe")
INNOEXTRACT = os.path.join(BIN, "innoextract.exe")


class FileHandler:
    def __init__(self, app: GenericApp):
        now_string = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H.%M.%S")
        self.__app = app
        self.__cache = os.path.join(app.target_dir, ".superelixier-cache")
        self.__staging = os.path.join(self.__cache, str(app.random_id))
        self.__keep_history = True
        self.__history = os.path.join(app.appdir, ".superelixier-history", now_string)
        self.__deferred = os.path.join(self.__cache, ".deferred", app.name)

    def __project_download(self):
        """
        Handle the download of blobs or check if deferred update matches the latest version on remote site.

        :return: False if the directory should be normalized, True if not.
        """
        # Check if deferred update files should be leveraged
        version_deferred = os.path.join(self.__deferred, "superelixier.json")
        if os.path.isfile(version_deferred):
            with open(version_deferred, "r") as file:
                version_deferred = json.load(file)
            if version_deferred == self.__app.version_latest:
                print(Ansi.GREEN + self.__app.name + ": Re-using previously downloaded update files")
                self.__staging = self.__deferred
                return True
            else:
                print(Ansi.GREEN + self.__app.name + ": Previously downloaded update is not latest version, removing")
                shutil.rmtree(self.__deferred)
        # Create folder structure if it doesn't exist
        os.makedirs(self.__staging, exist_ok=True)
        # Make sure staging directory is empty
        shutil.rmtree(self.__staging)
        os.mkdir(self.__staging)
        release_latest = self.__app.version_latest.blobs
        if len(release_latest) == 0:
            print("No matching downloads for the latest version")
        for url in release_latest:
            tmpfile = os.path.join(self.__staging, "download-incomplete")
            filename = Downloader(url, tmpfile).file
            if os.path.isfile(tmpfile):
                os.remove(tmpfile)
            archives = "001|7z|bz2|bzip2|gz|gzip|lzma|rar|tar|tgz|txz|xz|zip"
            if self.__app.definition.local.installer == "sfx":
                archives = f"exe|{archives}"
            if filename and re.fullmatch(f"^.*\\.({archives})$", filename.casefold()):
                subprocess.run([SEVENZIP, "x", "-aoa", filename], cwd=self.__staging, stdout=subprocess.DEVNULL)
                os.remove(os.path.join(self.__staging, filename))
                # Handle zipped installer case
                extracted = os.listdir(self.__staging)
                if len(extracted) == 1:
                    filename = extracted[0]
            if filename and filename.casefold().endswith(".exe"):
                if self.__app.definition.local.installer == "innoextract":
                    subprocess.run([INNOEXTRACT, "-n", filename], cwd=self.__staging, stdout=subprocess.DEVNULL)
                    os.remove(os.path.join(self.__staging, filename))
                elif self.__app.definition.local.installer is None:
                    os.rename(
                        os.path.join(self.__staging, filename), os.path.join(self.__staging, f"{self.__app.name}.exe")
                    )
        return False

    def __project_normalize(self):
        normalize_failure = False
        normalize_done = False
        while not normalize_done:
            extracted = os.listdir(self.__staging)
            if len(extracted) == 0:
                print(Ansi.ERROR + "Failure downloading or extracting this app" + Ansi.RESET)
                normalize_done = True
                normalize_failure = True
            elif len(extracted) == 1:
                extracted_content = os.path.join(self.__staging, extracted[0])
                if os.path.isdir(extracted_content):
                    for item in os.listdir(extracted_content):
                        shutil.move(os.path.join(extracted_content, item), os.path.join(self.__staging, item))
                    os.rmdir(extracted_content)
                elif os.path.isfile(extracted_content):
                    print(Ansi.BRIGHT + self.__app.name + ": file retrieved:")
                    print(extracted[0])
                    normalize_done = True
            elif len(extracted) > 1:
                print(Ansi.BRIGHT + self.__app.name + ": extracted files:")
                strs = []
                for extracted in extracted:
                    print_string = extracted
                    for pattern in self.__app.definition.local.delete:
                        if re.fullmatch(pattern, extracted):
                            print_string = Ansi.RED + extracted + " (removed)" + Ansi.RESET
                            full_path = os.path.join(self.__staging, extracted)
                            if os.path.isfile(full_path):
                                os.remove(full_path)
                            if os.path.isdir(full_path):
                                shutil.rmtree(full_path)
                    strs.append(print_string)
                print(", ".join(strs))
                normalize_done = True
        if not normalize_failure:
            new_installed = VersionInstalled(
                version_id=self.__app.version_latest.version_id,
                blobs=self.__app.version_latest.blobs,
                spec=self.__app.versioning_spec,
                repo=self.__app.definition.repo_type,
            )
            with open(os.path.join(self.__staging, "superelixier.json"), "w") as file:
                json.dump(new_installed.as_dict, file)

    def __project_merge_oldnew(self):
        # Data to keep
        keep_list = list_appdatas(self.__app)
        # Full dir tree list
        full_list = simple_folder_list(self.__staging)
        # Lock all files
        opened_files = lock_folder(self.__app, self.__staging, full_list)
        if opened_files is None:
            return False
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
                    # close file
                    if new_location in opened_files:
                        opened_files[new_location].close()
                    os.rename(new_location, history_location)
                    os.rename(stage_location, new_location)
                else:
                    os.replace(stage_location, new_location)
            else:
                os.rename(stage_location, new_location)
        for key in opened_files:
            opened_files[key].close()
        remove_empty_dirs(self.__staging)
        # Ideally don't create these folders in the first place:
        remove_empty_dirs(os.path.split(self.__history)[0], delete_top=True)
        return True

    def __defer_update(self):
        """
        If the new files couldn't be moved over (opened files in target), prepare update files for re-use next run.
        If the current job was already a deferred job, do nothing.
        """
        if self.__staging != self.__deferred:
            # Clear out possible orphaned files
            if os.path.isdir(self.__deferred):
                shutil.rmtree(self.__deferred)
            os.makedirs(os.path.split(self.__deferred)[0], exist_ok=True)
            os.rename(self.__staging, self.__deferred)

    def __post_install(self):
        """
        Actions to run after the boilerplate installation process.
        """
        if self.__app.name in ["VSCode", "VSCodium"]:
            os.makedirs(os.path.join(self.__app.appdir, "data"), exist_ok=True)

    def project_update(self):
        reused_files = self.__project_download()
        if not reused_files:
            self.__project_normalize()
        if not self.__project_merge_oldnew():
            self.__defer_update()
        self.__post_install()

    def project_install(self):
        reused_files = self.__project_download()
        if not reused_files:
            self.__project_normalize()
        if os.listdir(self.__staging):
            os.rename(self.__staging, self.__app.appdir)
        self.__post_install()
