"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import datetime
import os
import re
import shutil
import subprocess
from os.path import join as opj
from os.path import split as ops

from superelixier import configuration

APP_NAME = "superelixier"
VERSION = datetime.datetime.now().strftime("%Y-%m-%d")
PROJECT = os.path.normpath(os.path.dirname(__file__))
BUILD = opj(PROJECT, "build")
DIST = opj(PROJECT, "dist")
ROOT_FILES = [
    lic := opj(PROJECT, "LICENSE.txt"),
    notice := opj(PROJECT, "NOTICE.txt"),
    readme := opj(PROJECT, "README.md"),
]
FOLDERS = [
    BUILD,
    DIST,
    bin_dir := opj(PROJECT, "bin-win32"),
    bin_dist := opj(DIST, "bin-win32"),
    cfg_dir := opj(PROJECT, "config"),
    cfg_dist := opj(DIST, "config"),
    docs_dir := opj(PROJECT, "docs"),
    docs_dist := opj(DIST, "docs"),
    def_dir := opj(PROJECT, "definitions"),
    def_dist := opj(DIST, "definitions"),
    thirdparty_dir := opj(PROJECT, "thirdparty"),
    thirdparty_dist := opj(DIST, "thirdparty"),
]

os.chdir(PROJECT)


def cleanup():
    for folder in [BUILD, DIST]:
        if os.path.isdir(folder):
            shutil.rmtree(folder)


def conversion_copy(infile, dst):
    if re.match("^.*\\.md", infile.casefold()):
        outfile = ".".join(os.path.split(infile)[1].split(".")[:-1]) + ".html"
        pandoc(infile, opj(dst, outfile))
    else:
        os.makedirs(dst, exist_ok=True)
        shutil.copy(infile, dst)


def copy_folder(src, dst, exclusions=None):
    src_files = os.listdir(src)
    if exclusions:
        for exclude in exclusions:
            if exclude in src_files:
                src_files.remove(exclude)
    for src_file in src_files:
        if os.path.isdir(opj(src, src_file)):
            copy_folder(opj(src, src_file), opj(dst, src_file))
        else:
            conversion_copy(opj(src, src_file), dst)


def pandoc(src, dst):
    title = os.path.split(src)[-1].removeprefix(".md")
    preprocessed = opj(BUILD, ops(src)[1])
    with open(src, "r") as fd:
        markdown = fd.read()
    markdown = re.sub(r"\[(?P<text>.*?)]\((?P<href>.*?).md\)", r"[\g<text>](\g<href>.html)", markdown)
    with open(preprocessed, "w") as fd:
        fd.write(markdown)
    subprocess.run(
        [
            "pandoc",
            preprocessed,
            "--metadata",
            f'title="{title}"',
            "--standalone",
            "--output",
            dst,
            "--self-contained",
            "--css=./docs/github-markdown.css",
        ],
        cwd=PROJECT,
    )


cleanup()
configuration.write_app_list()
subprocess.run(
    ["pyinstaller", "src/superelixier/__main__.py", "--icon=assets/app.ico", "--name", APP_NAME, "--onefile"],
    cwd=PROJECT,
)
for f in FOLDERS:
    os.makedirs(f, exist_ok=True)
copy_folder(bin_dir, bin_dist)
copy_folder(cfg_dir, cfg_dist, exclusions=["auth.toml", "local.toml", "eula.toml"])
copy_folder(def_dir, def_dist)
copy_folder(docs_dir, docs_dist, exclusions=["example.png", "github-markdown.css"])
copy_folder(thirdparty_dir, thirdparty_dist)
for root_file in ROOT_FILES:
    conversion_copy(root_file, DIST)
subprocess.run(
    ["7z", "-tzip", "u", f"..\\..\\superelixier-updater-{VERSION}.zip", "*", "-m0=Deflate", "-mx9"], cwd=DIST
)
cleanup()
