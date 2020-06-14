import tkinter as tk
from tkinter import ttk
from Widgets import *

pagesRU = [
    'Парсер',
    'Регионайзер',
    'Анализатор',
    'Визуализатор'
]

"""
Class by Dmitry Podbolotov
"""
class Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, relief='flat', borderwidth=0, bd=-2, padx = 0, pady = 0)
        self.controller = controller
        self.scale = (1, 1)

    def resize(self, w, h, aw, ah):
        for child in self.children:
            if hasattr(child, 'resize'):
                child.resize(w, h, aw, ah)