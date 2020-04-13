from Gui.Widgets import *
from Gui.Page import *
import tkinter as tk
from tkinter import ttk
import json


class ChooseFilesPage(Page):
    filesToRead = []
    users = dict()
    image = None

    def __init__(self, parent, controller):

        super().__init__(parent, controller)
        self.scrollList = ScrollList(self, onclicked= lambda n: self.show_page(n))
        self.scrollList.grid(row = 0, column = 0)
        SimpleButton(self, onclicked= self.addFile).grid(row = 1, column = 0)

        canvas = tk.Canvas(self, width=300, height=245, bg='#F0F0ED')
        canvas.grid(row = 0, column = 1)
        self.image = tk.PhotoImage(file='Gui/user.png')
        container = tk.Frame(self, bd=-2)
        container.grid(row = 0, column = 1)
        canvas.create_image(150, 150, image=self.image, anchor='center')



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
        self.loadFiles()


    def loadFiles(self):
        progress = 0
        if self.filesToRead.__len__() > 0:
            step = 100 / self.filesToRead.__len__()
            for file in self.filesToRead:
                self.loadFile(file)
                progress += step
                # yield progress
            self.controller.update_users(self.users)
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