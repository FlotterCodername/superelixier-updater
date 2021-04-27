"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import time
from tkinter import *
from pygubu.widgets.tkscrolledframe import TkScrolledFrame

from config_loader.config_loader import ConfigLoader
from environment_handler.environment_handler import LockFile, LockFileException


class Configurator:
    def __init__(self):
        try:
            self.__lock = LockFile()
        except LockFileException:
            time.sleep(7)
            sys.exit()
        # Configuration
        configuration = ConfigLoader().configuration
        self.cfg_auth = configuration["auth"]
        self.cfg_available = configuration["available"]
        self.cfg_local = configuration["local"]

        self.toplevel = Tk()
        self.frame = Frame(self.toplevel)
        self.frame1 = Frame(self.frame)
        self.dropdown_frame = LabelFrame(self.frame1)
        __values = [key for key in self.cfg_local]
        self.dropdown = OptionMenu(self.dropdown_frame, __values[0], *__values, command=None)
        self.dropdown.pack(expand='true', fill='both', side='top')
        self.dropdown_frame.configure(background='#ffffff', labelanchor='nw', relief='flat',
                                      text='Install location	')
        self.dropdown_frame.grid(column='0', row='0', sticky='we')
        self.dropdown_frame.rowconfigure('0', pad='5')
        self.dropdown_frame.columnconfigure('0', minsize='0', pad='5', weight='2')
        self.confirm = Button(self.frame1)
        self.confirm.configure(compound='top', cursor='arrow', font='TkDefaultFont', relief='flat')
        self.confirm.configure(text='Save & Exit')
        self.confirm.grid(column='1', pady='5', row='0', sticky='se')
        self.confirm.rowconfigure('0', pad='5')
        self.confirm.columnconfigure('1', pad='5', weight='1')
        self.exit = Button(self.frame1)
        self.exit.configure(relief='flat', text='Exit without Saving')
        self.exit.grid(column='2', pady='5', row='0', sticky='se')
        self.exit.rowconfigure('0', pad='5')
        self.exit.columnconfigure('2', pad='5', weight='1')
        self.frame1.configure(background='#ffffff', height='200', width='200')
        self.frame1.pack(anchor='center', fill='both', padx='5', pady='5', side='top')
        self.frame2 = TkScrolledFrame(self.frame, scrolltype='both')
        self.placeholder = Text(self.frame2.innerframe)
        self.placeholder.configure(height='10', width='50')
        _text_ = '''text1'''
        self.placeholder.insert('0.0', _text_)
        self.placeholder.pack(side='top')
        self.frame2.innerframe.configure(background='#ffffff')
        self.frame2.configure(usemousewheel=False)
        self.frame2.pack(fill='both', side='bottom')
        self.frame.configure(background='#ffffff', height='360', width='568')
        self.frame.pack(fill='both', side='top')
        self.toplevel.configure(height='360', width='568')
        self.toplevel.title('Configure install locations')

        # Main window
        self.mainwindow = self.toplevel

    def run(self):
        self.mainwindow.mainloop()


if __name__ == '__main__':
    app = Configurator()
    app.run()
