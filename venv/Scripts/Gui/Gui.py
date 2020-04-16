from Gui.ChooseFilesPage import *
from Gui.Page import *
from Gui.RegionalizePage import *
from Gui.AnalyzerPage import *
import tkinter as tk
from tkinter import ttk

background_color = '#F0F0ED'

class Gui(tk.Tk):
    tempdir = ''
    page = ''
    pages = []
    page_number = 0  # 240 240 237

    def show(self, page):
        page.tkraise()

    def __init__(self):
        tk.Tk.__init__(self)
        self.initUI()

    def initUI(self):
        menubar = tk.Menu(self, bd=-2, borderwidth=0)
        self.config(menu=menubar, bd=-2, borderwidth=0)
        # pages = [ChooseFilesPage(f), RegionalizePage(f)]
        # for page in pages:
        #     page.place(in_=f, x=0, y=0, relwidth=1, relheight=1)
        # self.show(pages[0])
        # fileMenu = tk.Menu(menubar)
        # fileMenu.add_command(label="New", command=lambda: self.page.onNew)
        # fileMenu.add_command(label="Add file", command=lambda: self.page.addFile())
        # fileMenu.add_command(label="Add folder", command=lambda: self.page.addFolder)
        # fileMenu.add_command(label="Save", command=self.onSave)
        # fileMenu.add_command(label="Save as", command=self.onSaveAs)
        # fileMenu.add_command(label="Exit", command=self.onExit)
        # menubar.add_cascade(label="File", menu=fileMenu)

        style = ttk.Style()
        style.theme_create("mytheme", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [-2, -2, 0, 0]}},
            'Canvas': {'configure': {'bd' : -2}}
            }
                           )
        style.theme_use("mytheme")
        style = ttk.Style()
        style.layout('TNotebook.Tab', [])
        # turn off tabs
        self.container = tk.Frame(self, bd=-2)
        self.container.pack(expand=0, padx=0, pady=0)

        self.note = ttk.Notebook(self.container, padding=0)
        for F in (ChooseFilesPage, RegionalizePage, AnalyzerPage):
            frame = F(parent=self.note, controller=self)
            self.note.add(frame)
            self.pages.append(frame)
            # frame.grid(row=0, column=1, sticky="nsew")
            frame.configure(background=background_color)

        nb = NavBar(self.container, pages=['Loader', 'Regionalizer', 'Analyzer'], onclicked= lambda n: self.show_page(n))
        nb.pack(fill = 'both', padx = 0, pady = 0, side='top', expand=False)
        self.note.pack(expand=1, fill='both', padx=0, pady=0, side='bottom')
        self.show_page(1)

    def show_page(self, page_number):
        self.page_number = page_number
        self.note.select(page_number)


    def show_previous(self):
        self.page_number = self.page_number + 1 if self.page_number < self.pages.__len__() - 1 else 0
        self.note.select(self.page_number)

    def show_next(self):
        self.page_number = self.page_number - 1 if self.page_number > 0 else self.pages.__len__() - 1
        self.note.select(self.page_number)

    def onNew(self):
        self.tempdir = tempfile.gettempdir()

    def onOpen(self):
        print('')

    def onSave(self):
        print('')

    def onSaveAs(self):
        print('')

    def onExit(self):
        self.quit()

    def update_users(self, users):
        self.pages[1].update_users(users)

