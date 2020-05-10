from Gui.ChooseFilesPage import *
from Gui.Page import *
from Gui.RegionalizePage import *
from Gui.AnalyzerPage import *
from Gui.TablePage import *
import tkinter as tk
from tkinter import ttk
from threading import Timer

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
        # self.attributes('-alpha', 0.0)  # For icon
        # self.iconify()
        # window = tk.Toplevel(self)# Whatever size
        # self.overrideredirect(1)  # Remove border
        self.width = 0
        self.timer = None
        self.height = 0
        self.users = None
        self.initUI()

    def initUI(self):

        self.minsize(380, 330)
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
            "Tab": {"configure": []},
            'Canvas': {'configure': {'bd' : -2, 'highlightthickness' : 0}},
            "TFrame": {"configure": {'borderwidth': -10, 'highlightthicknes': 0}},
            "TNotebook": {
                "configure": {"background": 'red', "tabmargins": [-2, -2, -2, -2]}}
        }
                           )
        style.theme_use("mytheme")
        style = ttk.Style()
        style.layout('TNotebook.Tab', [])
        style.layout('TNotebook.padding', [])
        # turn off tabs
        self.container = tk.Frame(self, bd=-2, borderwidth = 0, highlightthickness=0, highlightbackground='red')
        self.container.pack(expand=1, fill=tk.BOTH, padx=0, pady=0)

        # self.note = ttk.Notebook(self.container, padding=0)
        self.note = Note(self.container)
        for F in (ChooseFilesPage, TablePage, RegionalizePage, AnalyzerPage):
            frame = F(parent=self.note, controller=self)
            self.note.add(frame)
            self.pages.append(frame)
            # frame.grid(row=0, column=1, sticky="nsew")
            frame.configure(background=background_color)

        self.nb = NavBar(self.container, pages=['Loader','Table', 'Regionalizer', 'Analyzer'], onclicked= lambda n: self.show_page(n))
        self.nb.pack(fill = 'both', padx = 0, pady = 0, side='top', expand=0)
        self.note.pack(expand=1, fill='both', padx=0, pady=0, side='bottom')
        self.note.select(0)
        self.page_number = 0



        self.container.bind("<Configure>", self.resize)

    def resize(self, e):
        if self.width > 0 and self.height > 0:
            if not self.page_changed:
                self.current_w = e.width
                self.current_h = e.height - self.nb.h
                if self.timer is not None:
                    self.timer.cancel()
                self.timer = Timer(0.1, lambda: self.note.resize(self.current_w, self.current_h, self.current_w / self.width, self.current_h / self.height))
                self.timer.start()
            else:
                # self.note.resize(e.width, e.height, e.width / self.width, e.height / self.height)
                self.page_changed = False
        else:
            self.height = e.height - self.nb.h
            self.width = e.width
            self.current_w = e.width
            self.current_h = e.height - self.nb.h
            self.note.resize(self.current_w, self.current_h, 1, 1, all = True)
            self.page_changed = False


    def show_page(self, page_number):
        self.page_number = page_number
        self.note.resize(self.current_w, self.current_h, self.current_w/self.width, self.current_h/self.height, all = True)
        self.page_changed = True
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
        users = users.reset_index(drop=True)
        self.users = users
        for page in self.pages:
            page.update_users(users)

    def get_users(self):
        return self.users
