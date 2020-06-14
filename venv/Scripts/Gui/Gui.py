from Gui.ChooseFilesPage import *
from Gui.Page import *
from Gui.RegionalizePage import *
from Gui.AnalyzerPage import *
from Gui.TablePage import *
import tkinter as tk
from tkinter import ttk
from threading import Timer
import pandas as pd

background_color = '#F0F0ED'


class Gui(tk.Tk):
    tempdir = ''
    page = ''
    pages = []
    page_number = 0  # 240 240 237
    page_changed = True

    def show(self, page):
        page.tkraise()

    def __init__(self):
        tk.Tk.__init__(self)
        self.width = 0
        self.timer = None
        self.height = 0
        self.users = None
        self.users_text = None
        self.initUI()

    def initUI(self):
        self.minsize(550, 380)
        menubar = tk.Menu(self, bd=-2, borderwidth=0)
        self.config(menu=menubar, bd=-2, borderwidth=0)

        style = ttk.Style()
        style.theme_create("mytheme", parent="alt", settings={
            "Tab": {"configure": []},
            'Canvas': {'configure': {'bd': -2, 'highlightthickness': 0}},
            "TFrame": {"configure": {'borderwidth': -10, 'highlightthicknes': 0}},
            "TNotebook": {
                "configure": {"background": 'red', "tabmargins": [-2, -2, -2, -2]}}
        }
                           )
        style.theme_use("mytheme")
        style = ttk.Style()
        style.layout('TNotebook.Tab', [])
        style.layout('TNotebook.padding', [])
        self.container = tk.Frame(self, bd=-2, borderwidth=0, highlightthickness=0, highlightbackground='red')
        self.container.pack(expand=1, fill=tk.BOTH, padx=0, pady=0)
        self.note = Note(self.container)
        for f in (ChooseFilesPage, TablePage, RegionalizePage, AnalyzerPage):
            frame = f(parent=self.note, controller=self)
            self.note.add(frame)
            self.pages.append(frame)
            frame.configure(background=background_color)

        self.nb = NavBar(self.container, pages=['Loader', 'Table', 'Regionalizer', 'Analyzer'],
                         onclicked=lambda n: self.show_page(n))
        self.nb.pack(fill='both', padx=0, pady=0, side='top', expand=0)
        self.note.pack(expand=1, fill='both', padx=0, pady=0, side='bottom')
        self.note.select(0)
        self.page_number = 0
        self.container.bind("<Configure>", self.resize)
        self.update_users(self.pages[0].users)

    def resize(self, e):
        if self.width > 0 and self.height > 0:
            if not self.page_changed:
                self.current_w = e.width
                self.current_h = e.height - self.nb.h
                if self.timer is not None:
                    self.timer.cancel()
                self.timer = Timer(0.1,
                                   lambda: self.note.resize(self.current_w, self.current_h, self.current_w / self.width,
                                                            self.current_h / self.height))
                self.timer.start()
            else:
                self.page_changed = False
        else:
            self.height = e.height - self.nb.h
            self.width = e.width
            self.current_w = e.width
            self.current_h = e.height - self.nb.h
            self.note.resize(self.current_w, self.current_h, 1, 1, all=True)
            self.page_changed = False

    def show_page(self, page_number):
        self.page_number = page_number
        self.note.resize(self.current_w, self.current_h, self.current_w / self.width, self.current_h / self.height,
                         all=True)
        self.page_changed = True
        self.note.select(page_number)

    def show_previous(self):
        self.page_number = self.page_number + 1 if self.page_number < self.pages.__len__() - 1 else 0
        self.note.select(self.page_number)

    def show_next(self):
        self.page_number = self.page_number - 1 if self.page_number > 0 else self.pages.__len__() - 1
        self.note.select(self.page_number)

    def update_users(self, users):
        users['sex'] = users['sex'].map(
            lambda a: ('M' if a == 2 else 'F' if a == 1 else 'NA') if isinstance(a, int) else a)
        self.users = users
        for page in self.pages:
            page.update_users(users)

    def get_users(self):
        return self.users

    def update_text(self, users_text):
        self.users_text = users_text

    def get_text(self):
        return self.users_text
