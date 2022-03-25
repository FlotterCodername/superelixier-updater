"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import sys
import tkinter

from dearpygui import dearpygui as dpg

from gui.component import Configurator

SCALE_FACTOR = 1


class SuGUI:
    __BLOCK_INPUT = False

    def __init__(self):
        self.__init_gui()
        self.__run_gui()

    @classmethod
    def block_input(cls):
        SuGUI.__BLOCK_INPUT = True

    @classmethod
    def __init_gui(cls):
        # Hidden tkinter initialization for use of native dialogs
        tkinter.Tk().withdraw()
        high_dpi_aware()
        dpg.create_context()
        dpg.configure_app(manual_callback_management=True)
        dpg.setup_dearpygui()
        with dpg.font_registry():
            p = os.path.join("..", "assets", "MotivaSans-Regular.ttf")
            default_font = dpg.add_font(p, 15 * SCALE_FACTOR)
        with dpg.window(tag="root"):
            dpg.bind_font(default_font)
        dpg.set_primary_window("root", True)

    @classmethod
    def __run_gui(cls, show="configurator"):
        title, width, height = "LOADING", 600, 800
        if show == "main_menu":
            pass
        elif show == "configurator":
            title, width, height = "Superelixier Updater Configurator", 600, 800
            Configurator()
        else:
            raise ValueError("Unknown view")
        dpg.create_viewport(title=title, width=width, height=height)
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            # insert here any code you would like to run in the render loop
            # you can manually stop by using stop_dearpygui()
            SuGUI.__render()
            dpg.render_dearpygui_frame()

    @classmethod
    def __render(cls):
        jobs = dpg.get_callback_queue()
        if jobs is not None:
            for job in jobs:
                result = dpg.run_callbacks((job,))
                if SuGUI.__BLOCK_INPUT:
                    SuGUI.__BLOCK_INPUT = False
                    break

    @classmethod
    def __del__(cls):
        dpg.destroy_context()


def high_dpi_aware():
    """
    https://docs.microsoft.com/en-us/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness
    """
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
            global SCALE_FACTOR
            SCALE_FACTOR = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        except OSError:
            pass


if __name__ == "__main__":
    SuGUI()
