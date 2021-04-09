"""
Copyright 2021 Fabian H. Schneider
"""
import colorama
import datetime
import json
import requests as rest
import os
import random
import re
import shutil
import string
import subprocess
import sys
import urllib.request as rq
from datetime import datetime

# TODO: Pre-Release version check
# TODO: Retention of old versions
# TODO: HTML Parse
# TODO: Buildbot

def print_header(string, color=''):
    bar = (len(string)+4)*"#"
    print(color + bar + "\n# " + string + " #\n"+ bar)


root = os.path.dirname(sys.argv[0])
os.chdir(root)
with open("available.json", 'r') as file:
    configurations = json.load(file)

for configuration in configurations:
    name = configuration["name"]
    user = configuration["user"]
    project = configuration["project"]
    blob_re = configuration["blob_re"]
    blob_unwanted = configuration["blob_unwanted"]
    appdatas = configuration["appdatas"]

    project_dir = os.path.join(root, name)
    random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
    staging = os.path.join(root, f".staging-{random_id}")
    old_version = os.path.join(root, f".oldver-{random_id}")
    os.chdir(root)

    releases = rest.get(f"https://api.github.com/repos/{user}/{project}/releases", headers=HEADERS)
    my_json = json.loads(releases.text)
    if releases.status_code != 200:
        print(f'HTTP Status {releases.status_code}: {my_json["message"]}')
        print(colorama.Fore.RED + f"Failed to update {name}")
        raise ValueError
    date_latest = datetime.strptime(my_json[0]["published_at"], GITHUB_DATE)

    def project_checkupdate():
        if os.path.isfile(os.path.join(project_dir, "superelixier.json")):
            with open(os.path.join(project_dir, "superelixier.json"), 'r') as file:
                date_installed = datetime.strptime(json.load(file), GITHUB_DATE)
            if date_latest == date_installed:
                return False
            elif date_latest > date_installed:
                return True
            else:
                print(colorama.Fore.RED + f"{name}: Could not determine installed version")
                raise ValueError
        else:
            print(colorama.Fore.MAGENTA + f"{name}: Version info file not found -- assuming update is available")
            return True

    def project_download():
        try:
            os.mkdir(staging)
        except FileExistsError:
            shutil.rmtree(staging)
            os.mkdir(staging)
        releases_latest = my_json[0]['assets']
        blob_list = []
        for blob in releases_latest:
            filename = blob['browser_download_url'].split("/")[-1]
            if re.fullmatch(blob_re, filename) is not None:
                blob_list.append(blob)
        if len(blob_list) == 0:
            print("No matching downloads for the latest version")
            raise ValueError
        for blob in blob_list:
            try:
                url = blob['browser_download_url']
                filename = url.split("/")[-1]
                print(f"Trying to get file from: {url}")
                rq.urlretrieve(url, os.path.join(root, staging, filename))
            except Exception:
                print("Failure downloading file")
            if re.fullmatch("^.*\\.(zip|rar|xz|7z)$", filename):
                subprocess.run(f"7z x -aoa {filename}", cwd=staging, stdout=subprocess.DEVNULL)
                os.remove(os.path.join(staging, filename))
            elif re.fullmatch("^.*\\.exe$", filename):
                os.rename(os.path.join(staging, filename), os.path.join(staging, f"{project}.exe"))

    def project_normalize():
        dirs_normalized = False
        while not dirs_normalized:
            extracted = os.listdir(staging)
            if len(extracted) == 0:
                print("Failure listing directory")
                raise FileNotFoundError
            elif len(extracted) == 1:
                extracted_dir = os.path.join(staging, extracted[0])
                if os.path.isdir(extracted_dir):
                    for file in os.listdir(extracted_dir):
                        shutil.move(
                            os.path.join(extracted_dir, file),
                            os.path.join(staging, file)
                            )
                    os.rmdir(extracted_dir)
                elif os.path.isfile:
                    dirs_normalized = True
            elif len(extracted) > 1:
                print_header(f"{name}: extracted files")
                strs = []
                for extracted in extracted:
                    print_string = extracted
                    for pattern in blob_unwanted:
                        if re.fullmatch(pattern, extracted):
                            print_string = colorama.Fore.RED + extracted + " (removed)" + colorama.Fore.RESET
                            os.remove(os.path.join(staging, extracted))
                    strs.append(print_string)
                print(", ".join(strs))
                dirs_normalized = True
        with open(os.path.join(staging, "superelixier.json"), "w") as file:
            json.dump(datetime.strftime(date_latest, GITHUB_DATE), file)

    def project_merge_oldnew():
        for appdata in appdatas:
            old_location = os.path.join(old_version, appdata)
            new_location = os.path.join(project_dir, appdata)
            if os.path.exists(old_location):
                if os.path.isfile(old_location):
                    os.replace(old_location, new_location)
                elif os.path.isdir(old_location):
                    os.rename(old_location, new_location)
            else:
                print(colorama.Fore.MAGENTA + f"Old {appdata} not found.")

    def project_update():
        print_header(f"{name}: Updating", color=colorama.Fore.GREEN)
        project_download()
        project_normalize()
        os.rename(project_dir, old_version)
        os.rename(staging, project_dir)
        project_merge_oldnew()
        shutil.rmtree(os.path.join(root, old_version))
        
    def project_install():
        print_header(f"{name}: Installing", color=colorama.Fore.BLUE)
        project_download()
        project_normalize()
        os.rename(staging, project_dir)

    if os.path.isdir(project_dir):
        if project_checkupdate():
            project_update()
        else:
            print(colorama.Style.BRIGHT + f"Up-to-date: {name}")
    else:
        project_install()
input("Press Enter to continue...")