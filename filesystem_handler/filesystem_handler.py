"""
Copyright 2021 Fabian H. Schneider
"""

import colorama
import json
import os
import re
import shutil
import subprocess
import urllib.request as rq

from github.github_project import GithubProject
from main import Main


class FilesystemHandler:

    def __init__(self, app: GithubProject):
        self.app = app
        self.staging = os.path.join(app.target_dir, f".staging-{app.random_id}")
        self.old_version = os.path.join(app.target_dir, f".oldver-{app.random_id}")

    def project_download(self):
        try:
            os.mkdir(self.staging)
        except FileExistsError:
            shutil.rmtree(self.staging)
            os.mkdir(self.staging)
        releases_latest = self.app.api_call[0]['assets']
        blob_list = []
        for blob in releases_latest:
            filename = blob['browser_download_url'].split("/")[-1]
            if re.fullmatch(self.app.blob_re, filename) is not None:
                blob_list.append(blob)
        if len(blob_list) == 0:
            print("No matching downloads for the latest version")
            raise ValueError
        for blob in blob_list:
            url = blob['browser_download_url']
            filename = url.split("/")[-1]
            print(f"Trying to get file from: {url}")
            rq.urlretrieve(url, os.path.join(self.app.target_dir, self.staging, filename))
            if re.fullmatch("^.*\\.(zip|rar|xz|7z)$", filename):
                subprocess.run(f"7z x -aoa {filename}", cwd=self.staging, stdout=subprocess.DEVNULL)
                os.remove(os.path.join(self.staging, filename))
            elif re.fullmatch("^.*\\.exe$", filename):
                os.rename(os.path.join(self.staging, filename), os.path.join(self.staging, f"{self.app.project}.exe"))

    def project_normalize(self):
        dirs_normalized = False
        while not dirs_normalized:
            extracted = os.listdir(self.staging)
            if len(extracted) == 0:
                print("Failure listing directory")
                raise FileNotFoundError
            elif len(extracted) == 1:
                extracted_dir = os.path.join(self.staging, extracted[0])
                if os.path.isdir(extracted_dir):
                    for file in os.listdir(extracted_dir):
                        shutil.move(
                            os.path.join(extracted_dir, file),
                            os.path.join(self.staging, file)
                        )
                    os.rmdir(extracted_dir)
                elif os.path.isfile:
                    dirs_normalized = True
            elif len(extracted) > 1:
                Main.print_header(f"{self.app.name}: extracted files")
                strs = []
                for extracted in extracted:
                    print_string = extracted
                    for pattern in self.app.blob_unwanted:
                        if re.fullmatch(pattern, extracted):
                            print_string = colorama.Fore.RED + extracted + " (removed)" + colorama.Fore.RESET
                            os.remove(os.path.join(self.staging, extracted))
                    strs.append(print_string)
                print(", ".join(strs))
                dirs_normalized = True
        with open(os.path.join(self.staging, "superelixier.json"), "w") as file:
            json.dump(self.app.date_latest, file)

    def project_merge_oldnew(self):
        for appdata in self.app.appdatas:
            old_location = os.path.join(self.old_version, appdata)
            new_location = os.path.join(self.app.appdir, appdata)
            if os.path.exists(old_location):
                if os.path.isfile(old_location):
                    os.replace(old_location, new_location)
                elif os.path.isdir(old_location):
                    os.rename(old_location, new_location)
            else:
                print(colorama.Fore.MAGENTA + f"Old {appdata} not found.")

    def project_update(self):
        Main.print_header(f"{self.app.name}: Updating", color=colorama.Fore.GREEN)
        self.project_download()
        self.project_normalize()
        os.rename(self.app.appdir, self.old_version)
        os.rename(self.staging, self.app.appdir)
        self.project_merge_oldnew()
        shutil.rmtree(os.path.join(self.app.target_dir, self.old_version))

    def project_install(self):
        Main.print_header(f"{self.app.name}: Installing", color=colorama.Fore.BLUE)
        self.project_download()
        self.project_normalize()
        os.rename(self.staging, self.app.appdir)
