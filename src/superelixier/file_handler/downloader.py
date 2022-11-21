"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import html
import os
import re
import string
from urllib.parse import urlparse, urlunparse

import requests
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier.helper.terminal import Ansi
from superelixier.html_page import HEADERS


class Downloader:
    def __init__(self, url, target):
        self._file = Downloader.__url_downloader(url, target)

    @classmethod
    def __url_downloader(cls, url, target) -> str | None:
        """
        curl without curl

        :param url:
        :return: remote filename
        """
        print(f"Downloading file from: {url}")
        try:
            url, response = Downloader.__handle_redirects(url, target)
            Downloader.__write_response(response, target)
            filename = os.path.join(os.path.split(target)[0], Downloader.__get_remote_filename(url, response))
            os.rename(target, filename)
            return filename
        except (RequestException, HTTPError, ValueError):
            return None

    @classmethod
    def __handle_redirects(cls, url, dl_file):
        """
        Handle redirects, status codes and JavaScript download trigger

        :param url:
        :return response:
        """
        response = requests.get(url, allow_redirects=True, headers=HEADERS, stream=True)
        if response.status_code != 200:
            print(Ansi.ERROR + "Download failed, HTTP status %s: %s" % (response.status_code, response.reason))
            raise HTTPError
        else:
            if response.headers.get("refresh"):
                old_url = url
                url = response.headers["refresh"].split(";")[-1]
                if "url=" in url.lower():
                    url = url.split("=")[-1]
                    url = Downloader.normalize_url(url, source=old_url)
                    print(f"Redirected to: {url}")
                    url, response = Downloader.__handle_redirects(url, dl_file)
                else:
                    print("Failed to find URL on redirect")
                    raise ValueError
            elif response.headers.get("content-type"):
                ct = response.headers["content-type"]
                if "text/html" in ct.lower():
                    old_url = url
                    javascript_download = "{window.location *= *('|\")(.*)('|\");*\\}"
                    Downloader.__write_response(response, dl_file)
                    with open(dl_file, "r") as file:
                        html_response = file.read()
                    match = re.search(javascript_download, html_response)
                    if match:
                        url = Downloader.normalize_url(match.group(2), source=old_url)
                        print(f"Redirected to: {url}")
                        if not Downloader.__check_domain(old_url, url):
                            print(
                                f"{Ansi.ERROR}Could not do a JavaScript-triggered download because the download domain "
                                "didn't match a trusted domain we know."
                            )
                            raise ValueError
                        url, response = Downloader.__handle_redirects(url, dl_file)
                    else:
                        print("Failed to find URL on redirect")
                        raise ValueError
        return url, response

    @classmethod
    def __write_response(cls, response, file):
        with open(file, "wb") as fd:
            for chunk in response.iter_content(chunk_size=1024):
                fd.write(chunk)

    @classmethod
    def normalize_url(cls, url, source=None):
        """
        Handling for relative URL paths

        :param url:
        :param source:
        """
        skeleton = [None, None, None, None, None, None]
        try:
            url_parsed = urlparse(html.unescape(url), scheme="https")
            if source:
                source_parsed = urlparse(html.unescape(source), scheme="https")
            else:
                source_parsed = skeleton
            for i in range(6):
                skeleton[i] = url_parsed[i]
                if i < 2 and skeleton[i] == "":
                    skeleton[i] = source_parsed[i]
            if None in skeleton[0:5]:
                raise ValueError
            url = urlunparse(skeleton)
        except Exception:
            print(Ansi.ERROR + "Failed to build URL")
            raise ValueError
        return url

    @classmethod
    def __check_domain(cls, old_url: str, new_url: str) -> bool:
        # I considered slicing to second-level domain and TLD here.
        # But since the list of [PSDs](https://publicsuffix.org/) is ever-expanding...
        # This will have to do until I have a safe method to handle PSDs.
        if urlparse(old_url).netloc == urlparse(new_url).netloc:
            return True
        else:
            return False

    @classmethod
    def __get_remote_filename(cls, url, response):
        cd = response.headers.get("content-disposition")
        if cd:
            filename = re.findall("filename=(.+)", cd)[0]
        else:
            filename = url.split("/")[-1]
            if re.search("^.*?\\.(exe|001|7z|bz2|bzip2|gz|gzip|lzma|rar|tar|tgz|txz|xz|zip)\\?", filename):
                filename = filename.split("?")[0]
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = "".join(c for c in filename if c in valid_chars)
        return filename

    @property
    def file(self):
        return self._file
