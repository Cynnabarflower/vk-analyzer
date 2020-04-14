from Gui.Widgets import *
from Gui.Page import *
import Gui.Gui as Gui
import tkinter as tk
from tkinter import ttk
import json

class ChooseFilesPage(Page):

    SCROLL_ITEM_HEIGHT = 105
    SCROLL_ITEM_WIDTH = 245
    SCROLL_ITEM_PADDING_X = 10
    SCROLL_ITEM_PADDING_Y = 10
    SCROLL_PADDING = 10

    filesToRead = []
    users = dict()
    image = None
    loadedfiles = 0

    def __init__(self, parent, controller):

        super().__init__(parent, controller)
        self.scrollList = ScrollList(self, onclicked= lambda n: self.show_page(n), padding = 20, w= self.SCROLL_ITEM_WIDTH, h=SCROLL_ITEM_HEIGHT  )
        self.scrollList.grid(row = 0, column = 0)
        SimpleButton(self, onclicked= self.addFile).grid(row = 1, column = 0)

        self.userscanvas = canvas = tk.Canvas(self, width=265, height=265, bg=Gui.background_color, bd=-2)
        canvas.grid(row = 0, column = 1)
        padding = 20
        round_rectangle(canvas, padding, padding, 265 - padding, 265 - padding, radius=64, fill = '#91b0cf')
        self.image = tk.PhotoImage(file='Gui/user140.png')
        canvas.create_image(265/2, (265 - 2 * padding)*40/100 + padding, image=self.image, anchor='center')
        self.userscountertext = canvas.create_text(265/2, padding + (265 - 2*padding)*85/100, text='12345678', font=('Colibri', 26), fill = '#ffffff')

        w = 265
        h = BUTTON_HEIGHT + 2*PADDING
        self.filescanvas = canvas = tk.Canvas(self, width=w, height=h, bg='#F0F0ED')
        canvas.grid(row=1, column=1)
        self.filescountertext = canvas.create_text(w / 2, h/2,
                                                   text='', font=('Colibri', 22), fill='#7389a1')
        self.filescanvas.itemconfig(self.filescountertext, text=(
                str(self.loadedfiles) + " files loaded"))
        self.userscanvas.itemconfig(self.userscountertext, text=str(self.users.__len__()))
        self.update()



        # self.listBox = tk.Listbox(self, selectmode=tk.EXTENDED)
        # self.listBox.grid(row=10, column=0, rowspan=4)
        # button1 = tk.Button(self, text="Add file",
        #                     command=lambda: self.addFile())
        # button1.grid(row=10, column=1)
        # button1 = tk.Button(self, text="Add folder",
        #                     command=lambda: self.addFolder())
        # button1.grid(row=11, column=1)
        # self.progressButton = ProgressButton(parent=self, onclicked=self.loadFiles, text='Load files')
        # self.progressButton.grid(row=16, column=0)

    def addFile(self):
        addedFiles = tk.filedialog.askopenfilenames(title="Select vka file",
                                                    filetypes=([("All", "*.*"), ("vka", "*.vka")]))
        for addedFile in addedFiles:
            for f in self.filesToRead:
                if f == addedFile:
                    # addedFile = ''
                    break
            if addedFile:
                self.filesToRead += [addedFile]
                self.scrollList.add(addedFile.split('/')[-1])
        self.filescanvas.itemconfig(self.filescountertext, text=(str(self.loadedfiles)+" of "+str(self.loadedfiles+self.filesToRead.__len__())+" loaded..."))
        self.loadFiles()


    def loadFiles(self):
        progress = 0
        if self.filesToRead.__len__() > 0:
            for file in self.filesToRead:
                self.loadFile(file)
                progress += 1
                self.loadedfiles += 1
                print(self.loadedfiles)
                self.filescanvas.itemconfig(self.filescountertext, text=(
                            str(progress) + " of " + str(self.filesToRead.__len__()) + " loaded..."))
                self.update_users()
                self.update()

                # yield progress
            self.filesToRead = []
            self.filescanvas.itemconfig(self.filescountertext, text=(
                    str(self.loadedfiles) + " files loaded"))

        # print('files loaded')

    def loadFile(self, file):
        f = open(file, 'r')
        filename = file.split('/')[-1]
        counter = 0
        js_packs = json.load(f)
        total = js_packs.__len__()
        for js in js_packs:
            for user in js:
                if user['id'] in self.users:
                    self.users[user['id']] += [user]
                else:
                    self.users[user['id']] = [user]
            counter += 1
            self.scrollList.setProgress(name = filename, progress = counter/total)

    def update_users(self):
        self.userscanvas.itemconfig(self.userscountertext, text=str(self.users.__len__()))
        self.controller.update_users(self.users)