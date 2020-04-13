import tkinter as tk
from tkinter import ttk
from Gui.Widgets import *

pagesRU = [
    'Парсер',
    'Регионайзер',
    'Анализатор',
    'Визуализатор'
]

class Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, relief='flat', borderwidth=0, bd=-2, padx = 0, pady = 0)
        self.controller = controller
        # nb = NavBar(self, pages=pagesRU, onclicked= lambda n: self.setPage(n))
        # nb.grid(row=0, column=0)



    def setPage(self, n):
        self.controller.show_page(n)
