"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os.path
import uuid
from copy import deepcopy
from os.path import join as opj
from typing import Callable, Collection

from dearpygui import dearpygui as dpg

from gui.callbacks import fake_callback
from helper import DIR_APP


class Component:
    def __init__(self):
        self.__tag = tagme()
        self.__parent = self.__set_parent()
        self.__layout = []

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def parent(self) -> str:
        return self.__parent

    @staticmethod
    def __set_parent(parent: str = None):
        if not parent:
            parent = "root"
        return parent

    def add_child(self, **kwargs):
        pass

    def update(self):
        pass

    def __del__(self):
        for c in self.__layout:
            c.__del__()


class Button(Component):
    def __init__(self, label: str, callback: Callable):
        super().__init__()
        dpg.add_button(label=label, parent=self.parent, callback=callback)


class LibraryFolder(Component):
    def __init__(self, path: str, apps: Collection[str] = ()):
        super().__init__()
        self.apps = apps
        self.table_tag: str = tagme()
        dpg.add_collapsing_header(label=path, parent=self.parent, tag=self.tag, default_open=True)
        dpg.add_button(label="[+] Select apps to add...", parent=self.tag)
        with dpg.table(
            header_row=False,
            resizable=False,
            policy=dpg.mvTable_SizingStretchProp,
            parent=self.tag,
            tag=self.table_tag,
        ):
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
        self.update()

    def update(self):
        for app in self.apps:
            with dpg.table_row(parent=self.table_tag):
                with dpg.table_cell():
                    dpg.add_button(label=app, callback=fake_callback)
                with dpg.table_cell():
                    dpg.add_button(label="Delete app", callback=fake_callback)
                with dpg.table_cell():
                    dpg.add_button(label="Disable updating", callback=fake_callback)


class MainMenu(Component):
    def __init__(self):
        super().__init__()


class Configurator(Component):

    CFG_DIR = opj(DIR_APP, "..", "config")

    def __init__(self):
        super().__init__()
        with open(opj(Configurator.CFG_DIR, "local.json"), "r") as fd:
            self._cfg_old = json.load(fd)
        self._cfg_new = deepcopy(self._cfg_old)
        Button(label="[+] Add app library folder...", callback=self.add_lib_folder)
        Button(label="Undo all", callback=self.undo)
        self.update()

    def update(self):
        for key in self._cfg_new:
            LibraryFolder(path=key, apps=self._cfg_new[key])

    def add_lib_folder(self):
        from tkinter import filedialog

        folder = filedialog.askdirectory()
        if folder and os.path.isdir(folder):
            self._cfg_new[folder.replace("\\", "/")] = []
            self.update()

    def undo(self):
        self._cfg_new = deepcopy(self._cfg_old)
        self.update()


def tagme():
    return str(uuid.uuid4())
