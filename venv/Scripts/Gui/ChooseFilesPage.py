from Gui.Widgets import *
from Gui.Page import *
import Gui.Gui as Gui
import tkinter as tk
from tkinter import ttk
import json
from multiprocessing import Queue
from threading import Thread

class ChooseFilesPage(Page):

    SCROLL_ITEM_HEIGHT = 50
    SCROLL_ITEM_WIDTH = 245
    SCROLL_ITEM_PADDING_X = 10
    SCROLL_ITEM_PADDING_Y = 10
    SCROLL_PADDING = 20
    SCROLL_WIDTH = SCROLL_ITEM_WIDTH + 2 * SCROLL_ITEM_PADDING_X
    SCROLL_HEIGHT = (SCROLL_ITEM_HEIGHT + SCROLL_ITEM_PADDING_Y) * 4
    WINDOW_WIDTH = 530
    WINDOW_HEIGHT = 360

    filesToRead = []
    users = dict()
    image = None
    loadedfiles = 0

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.scrollList = ScrollList(self, onclicked= lambda n: self.show_page(n), item_height=self.SCROLL_ITEM_HEIGHT, item_padding=self.SCROLL_ITEM_PADDING_Y, padding =(self.SCROLL_PADDING), w= self.SCROLL_WIDTH, h=self.SCROLL_HEIGHT)
        self.scrollList.grid(row = 0, column = 0)
        self.add_button = SimpleButton(self, onclicked= self.addFile, text = '+')
        self.add_button.grid(row = 1, column = 0)


        self.userscanvas = canvas = tk.Canvas(self, width=285, height=265, bg=Gui.background_color, bd=-2)
        canvas.grid(row = 0, column = 1)
        padding = 20
        round_rectangle(canvas, padding, padding, 265 - padding, 265 - padding, radius=64, fill = '#91b0cf')
        self.image = tk.PhotoImage(file='Gui/user140.png')
        canvas.create_image(265/2, (265 - 2 * padding)*40/100 + padding, image=self.image, anchor='center')
        self.userscountertext = canvas.create_text(265/2, padding + (265 - 2*padding)*85/100, text='12345678', font=('Colibri', 26), fill = '#ffffff')
        self.last_scale = (1,1)
        w = 265
        h = BUTTON_HEIGHT + 2*PADDING
        self.filescanvas = canvas = tk.Canvas(self, width=w, height=h, bg='#F0F0ED')
        canvas.grid(row=1, column=1)
        self.filescountertext = canvas.create_text(w / 2, h/2,
                                                   text='', font=('Colibri', 22), fill='#91b0cf')
        self.filescanvas.itemconfig(self.filescountertext, text=(
                str(self.loadedfiles) + " files loaded"))
        self.userscanvas.itemconfig(self.userscountertext, text=str(self.users.__len__()))
        self.update()


    def resize(self, w, h, aw, ah):
        print('FilePage resized',w, h, aw, ah)
        self.add_button.resize(aw, ah)
        self.scrollList.resize(w, h, aw, ah)
        self.userscanvas.configure(width=aw * 285, height=ah * 265)
        self.filescanvas.configure(width=aw * 265, height=ah * (BUTTON_HEIGHT + 2*PADDING))
        current_scale = (aw / self.last_scale[0], ah / self.last_scale[1])
        self.userscanvas.scale('all', 0, 0, current_scale[0], current_scale[1])
        self.filescanvas.scale('all', 0, 0, current_scale[0], current_scale[1])
        self.last_scale = (aw, ah)

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
        self.load_files_launch()

    def load_files_launch(self):
        q = Queue()
        Thread(target=self.loadFiles, args=[q], daemon=True).start()
        current_filename = ''
        while True:
            rep = q.get()
            print(str(rep))
            if rep == 'DONE':
                break
            if rep.__len__() == 2:
                filename = rep[0]
                progress = rep[1]
                self.scrollList.setProgress(name=filename, progress=progress)
            else:
                self.loadedfiles = rep[0]
                self.update_users()
                self.filescanvas.itemconfig(self.filescountertext, text=(
                        str(self.loadedfiles) + " of " + str(self.filesToRead.__len__()) + " loaded..."))
                self.update()
        self.filesToRead = []
        self.filescanvas.itemconfig(self.filescountertext, text=(
                str(self.loadedfiles) + " files loaded"))
        q.close()

    def loadFiles(self, q):
        progress = 0
        if self.filesToRead.__len__() > 0:
            for file in self.filesToRead:
                self.loadFile(file, q)
                progress += 1
                q.put([progress])
                # yield progress
        q.put('DONE')



        # print('files loaded')

    def loadFile(self, file, q):
        q.put([file, 0])
        import time as t
        f = open(file, 'r')
        print(t.time())
        filename = file.split('/')[-1]
        counter = 0
        js_packs = json.load(f)
        total = js_packs.__len__()
        for js in js_packs:
            for user in js:
                if user['id'] in self.users:
                    if self.users[user['id']].__len__() < user.__len__():
                        self.users[user['id']] = user
                else:
                    self.users[user['id']] = user
            counter += 1
            q.put((filename, counter/total))
        self.after(100, lambda: self.scrollList.remove(name = filename))

    def update_users(self):
        self.userscanvas.itemconfig(self.userscountertext, text=str(self.users.__len__()))
        self.controller.update_users(self.users)