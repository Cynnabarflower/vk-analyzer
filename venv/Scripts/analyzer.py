import json
import pandas
import os
import matplotlib.pyplot as pyplot
import matplotlib.cm as cm
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import tempfile
from threading import Thread
import time
import random
import threading
import math

# data_frame = pandas.read_csv('C:/Users/Dmitry/PycharmProjects/untitled/venv/Scripts/' + 'Onlineonline_map_sum2.csv')


def someFoo():
    for id in online_map:
        series = pandas.Series(online_map[id])
        series.name = str(id)
        data_frame = data_frame.append(series)
    for id in online_map:
        for el in online_map[id]:
            el['online'] = str(el['online'])
            el['scan'] = str(el['scan'])
    f = open(dirs[0] + 'online_map3.txt', 'w')
    json.dump(online_map, f)
    f.flush()
    f.close()
    data_frame.groupby(['city_name'])['id'].count().plot(kind='bar')
    pyplot.show()
    data_frame.groupby(['sex'])['id'].count().plot(kind='bar')
    pyplot.show()
    data_frame.groupby(['first_name'])['id'].count().plot(kind='bar')
    # data_frame['first_name'].plot()
    pyplot.show()
    # print(data_frame.to_string())
    print('done')


def getData(dir):
    if not dir.endswith('/'):
        dir += '/'
    conversationPath = dir + 'conversations/'
    usersPath = dir + 'users/'
    data_frame = pandas.DataFrame()
    data_frame['photos'] = None
    data_frame['posts'] = None
    data_frame['city_name'] = None

    if (True):
        if (os.path.exists(usersPath)):
            fileTree = os.walk(usersPath)
            for userFolders in fileTree:
                for userFolder in userFolders[1]:
                    userFolderName = userFolders[0] + userFolder
                    if os.path.exists(userFolderName + '/info.txt'):
                        userInfo = json.load(open(userFolderName + '/info.txt'))
                        series = pandas.Series(userInfo)
                        series.name = str(userInfo['id'])
                        data_frame = data_frame.append(series)
                        if 'city' in userInfo:
                            data_frame.at[str(userIЦnfo['id']), 'city_name'] = userInfo['city']['title']
                        if os.path.exists(userFolderName + '/info.txt'):
                            # userPhotos = json.load(open(userFolderName + '/photos.txt'))
                            data_frame.at[str(userInfo['id']), 'photos'] = 'userPhotos'
                        if (os.path.exists(userFolderName + '/posts.txt')):
                            # userPosts = json.load(open(userFolderName+'/posts.txt'))
                            data_frame.at[str(userInfo['id']), 'posts'] = 'userPosts'

            data_frame.groupby(['city_name'])['id'].count().plot(kind='bar')
            pyplot.show()
            data_frame.groupby(['sex'])['id'].count().plot(kind='bar')
            pyplot.show()
            data_frame.groupby(['first_name'])['id'].count().plot(kind='bar')
            # data_frame['first_name'].plot()
            pyplot.show()
            return

    words = dict()
    series = None
    if (os.path.exists(conversationPath)):
        conversationFiles = os.walk(conversationPath)
        for files in conversationFiles:
            for file in files[2]:
                obj = json.load(open(files[0] + file, 'r'))
                if (obj):
                    messages = obj[0]
                    for message in messages:
                        if 'text' in message and message['text']:
                            message_words = message['text'].split()
                            for word in message_words:
                                if len(word) < 3 or len(word) > 20:
                                    continue
                                word = word.lower()
                                while len(word) > 0 and not word[0].isalpha():
                                    word = word[1:]
                                while len(word) > 0 and not word[len(word) - 1].isalpha():
                                    word = word[:-1]
                                if not word:
                                    continue
                                if word in words:
                                    words[word] = words[word] + 1
                                else:
                                    words.update({word: 1})
        series = pandas.Series(words)
        series.name = 'count'
        df = pandas.DataFrame(series).sort_values('count', ascending=False)

        print(df.to_string())

        df[:40].plot(kind='bar')
        pyplot.show()


def getPlainTextFromMessages(dataFrame):
    return ''


def getSex(dir):
    data_frame = pandas.DataFrame()
    if not dir.endswith('/'):
        dir += '/'
    fileTree = os.walk(dir)
    fileTree.__next__()
    for onlineFolders in fileTree:
        for onlineFile in onlineFolders[2]:
            onlineData = json.load(open(fileName))
            loaded = 0
            for id in onlineData:
                loaded += 1
                if loaded % 1000:
                    print(loaded)
                    break
                series = pandas.Series(onlineData[id])
                series.name = str(id)
                data_frame = data_frame.append(series)

    data_frame.plot(kind='bar')
    pyplot.show()


class ProgressButton(tk.Frame):
    def __init__(self, parent, w = 120, h = 26, backgroundcolor = '#ffffff',  onclicked = lambda e: None, text = '', textcolor = '#000000', fillcolor = "#44ff44"):
        tk.Frame.__init__(self, parent)
        self.w = w
        self.h = h
        self.text = text
        self.textcolor = textcolor
        self.backgroundcolor = backgroundcolor
        self.fillcolor = fillcolor
        self.onclicked = onclicked
        c = tk.Canvas(self, width=w, height=h, bg=backgroundcolor)
        c.bind("<Button-1>", self.clicked)
        c.pack()
        self.canvas = c
        self.initcanvas()


    def clicked(self, e):
        gen = self.onclicked()
        i = 100
        for i in gen:
            print(i)
            self.drawProgress(i)
            self.update()
        if i < 100:
            self.drawProgress(100)

    def initcanvas(self):
        self.canvas.delete('all')
        # self.canvas.create_rectangle(0, 0, prorgess / 100 * self.w, self.h, outline=self.backgroundcolor, fill=self.backgroundcolor)
        self.canvas.create_text(self.w / 2, self.h / 2, text=self.text, fill=self.textcolor)

    def drawProgress(self, prorgess):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, prorgess/100*self.w, self.h, outline=self.fillcolor, fill=self.fillcolor)
        if prorgess < 100:
            self.canvas.create_text(self.w/2, self.h/2, text=str(math.floor(prorgess))+'%', fill=self.textcolor)
        else:
            self.canvas.create_text(self.w / 2, self.h / 2, text=str('done!'), fill=self.textcolor)
            self.after(1000, self.initcanvas)

class Gui(tk.Tk):

    tempdir = ''
    page = ''
    pages = []
    page_number = 0

    def show(self, page):
        page.tkraise()

    def __init__(self):
        tk.Tk.__init__(self)
        self.initUI()

    def initUI(self):

        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # pages = [ChooseFilesPage(f), RegionalizePage(f)]
        # for page in pages:
        #     page.place(in_=f, x=0, y=0, relwidth=1, relheight=1)
        # self.show(pages[0])
        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="New", command=lambda: self.page.onNew)
        fileMenu.add_command(label="Add file", command=lambda: self.page.addFile())
        fileMenu.add_command(label="Add folder", command=lambda: self.page.addFolder)
        fileMenu.add_command(label="Save", command=self.onSave)
        fileMenu.add_command(label="Save as", command=self.onSaveAs)
        fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for F in (ChooseFilesPage, RegionalizePage):
            frame = F(parent=container, controller=self)
            self.pages.append(frame)
            frame.grid(row=0, column=0, sticky="nsew")
            self.show_page(0)

    def show_page(self, page_number):
        self.page_number = page_number
        page = self.pages[page_number]
        page.tkraise()

    def show_previous(self):
        self.page_number = self.page_number + 1 if self.page_number < self.pages.__len__() -1 else 0
        page = self.pages[self.page_number]
        page.tkraise()

    def show_next(self):
        self.page_number = self.page_number - 1 if self.page_number > 0 else self.pages.__len__()-1
        page = self.pages[self.page_number]
        page.tkraise()

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



class ChooseFilesPage(tk.Frame):

    filesToRead = []
    users = dict()


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.listBox = tk.Listbox(self, selectmode=tk.EXTENDED)
        self.listBox.grid(row = 0, column = 0, rowspan=4)
        button1 = tk.Button(self, text="Add file",
                            command=lambda: self.addFile())
        button1.grid(row = 0, column = 1)
        button1 = tk.Button(self, text="Add folder",
                            command=lambda: self.addFolder())
        button1.grid(row = 1, column = 1)
        self.progressButton = ProgressButton(parent=self, onclicked=self.loadFiles, text='Load files')
        self.progressButton.grid(row=6, column = 0)
        button1 = tk.Button(self, text=">",
                            command=lambda: controller.show_next())
        button1.grid(row = 7, column = 2)

    def addFile(self):
        addedFiles = tk.filedialog.askopenfilenames(title="Select vka file",
                                               filetypes=([ ("All", "*.*"), ("vka", "*.vka")]))
        for addedFile in addedFiles:
            for f in self.filesToRead:
                if f == addedFile:
                    #addedFile = ''
                    break
            if addedFile:
                self.filesToRead += [addedFile]
                self.listBox.insert(tk.END, addedFile.split('/')[-1] + ' (' + addedFile + ')')

    def addFolder(self):
        addedDir = tk.filedialog.askdirectory(initialdir="/", title="Select vka file")
        for f in self.filesToRead:
            if f == addedDir:
                addedDir = ''
                break
        if addedDir:
            self.filesToRead += [addedDir]
            self.listBox.insert(END, addedFile.split('/')[-1] + ' (' + addedFile + ')')


    def loadFiles(self):
        progress = 0
        if self.filesToRead.__len__() > 0:
            step = 100/self.filesToRead.__len__()
            for file in self.filesToRead:
                self.loadFile(file)
                progress += step
                yield progress
            self.controller.update_users(self.users)
        # print('files loaded')

    def loadFile(self, file):
        f = open(file, 'r')
        js_packs = json.load(f)
        for js in js_packs:
            for user in js:
                if user['id'] in self.users:
                    self.users[user['id']] += [user]
                else:
                    self.users[user['id']] = [user]


class RegionalizePage(tk.Frame):

    users = dict()
    regions = {}
    regions_lock = threading.Lock()

    # color_gradient = [
    #     "#5AABF6",
    #     "#51A0EA",
    #     "#4896DE",
    #     "#3F8BD2",
    #     "#3681C6",
    #     "#2D76BB",
    #     "#246CAF",
    #     "#1B61A3",
    #     "#125797",
    #     "#094C8B",
    #     "#004280"
    # ]

    color_gradient = [
        "#5AABF6",
        "#3F8BD2",
        "#246CAF",
        "#094C8B",
    ]

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.regions_coordinates = json.load(open('allCoordinates.json', 'r'))
        for reg in self.regions_coordinates:
            for poly in reg['coordinates'][0]:
                for point in poly:
                    t = point[0]
                    point[0] = point[1]
                    point[1] = t
        c = tk.Canvas(self, width=800, height=400, bg='white')
        c.pack()
        self.canvas = c
        self.draw_map()

        button1 = tk.Button(self, text="regionalize",
                            command=lambda: self.regionalize())
        button1.pack()

        button1 = tk.Button(self, text="<",
                            command=lambda: controller.show_previous())
        button2 = tk.Button(self, text=">",
                            command=lambda: controller.show_next())
        button1.pack()
        button2.pack()

    def draw_map(self, loop = True, draw_labels = False):
        if self.controller.page_number == 1:
            c = self.canvas
            c.delete('all')
            coords = self.regions_coordinates
            minreg = 999999
            maxreg = -99
            with self.regions_lock:
                regions = self.regions.copy()

            for reg in regions:
                minreg = min(minreg, self.regions[reg])
                maxreg = max(maxreg, self.regions[reg])

            for reg in coords:
                drawQuan = True
                for poly in reg['coordinates'][0]:
                    if reg['name'] in regions:
                        try:
                            regcolor = self.color_gradient[round((regions[reg['name']]-minreg)/(maxreg-minreg)*(self.color_gradient.__len__()-1))]
                        except Exception as e:

                            print(minreg, ' ', maxreg, ' ', regions[reg['name']], ' ', round(
                                (regions[reg['name']] - minreg) / (maxreg - minreg) * (self.color_gradient.__len__() - 1)))

                    else:
                        regcolor = '#DDDDDD'
                    poly_coords = []
                    scaleX = 4
                    scaleY = scaleX * 5 / 3
                    polyminx = 9999
                    polymaxx = -99
                    polyminy = 9999
                    polymaxy = -99
                    for point in poly:
                        if drawQuan:
                            polymaxx = max(point[1] * scaleX, polymaxx)
                            polyminx = min(point[1] * scaleX, polyminx)
                            polymaxy = max((90 - point[0]) * scaleY, polymaxy)
                            polyminy = min((90 - point[0]) * scaleY, polyminy)
                        poly_coords += [point[1] * scaleX, (90 - point[0]) * scaleY]
                    c.create_polygon(poly_coords, fill=regcolor, outline='black')
                    if drawQuan and draw_labels:
                        c.create_text((polyminx+polymaxx)/2, (polyminy+polymaxy)/2, text = str(regions[reg['name']]) if reg['name'] in regions else '')
                        drawQuan = False
        if (loop):
            self.after(400, self.draw_map)

    def update_users(self, users):
        self.users = users

    def regionalize(self):
        self.regions = {}
        u_len = self.users.__len__()
        users_list = list(self.users.values())
        i = 0
        cities = json.load(open('citiesMap.json', 'r'))
        cities['1'] = {'region': 'RU-MOS'}
        cities['2'] = {'region': 'RU-LEN'}

        threads = []
        step = min(50000, round(u_len))
        while i < u_len:
            threads.append(Thread(target=self.__reg, args=([users_list, cities, i, min(u_len, i+step), i]), daemon= True))
            i += min(u_len, step)
        for th in threads:
            th.start()


    def __reg(self, users_list, cities, a, b, name):
        not_found = {}
        regs = {}
        for i in range(a, b):
            if ('city' in users_list[i][0]):
                city_id = str(users_list[i][0]['city']['id'])
                if city_id in cities:
                    reg = cities[city_id]['region']
                    if reg in regs:
                        regs[reg] += 1
                    else:
                        regs[reg] = 1
                else:
                    not_found[city_id] = ''
        time.sleep(random.randint(1, 10) * 0.5)
        with self.regions_lock:
            for reg in regs:
                if reg in self.regions:
                    self.regions[reg] += regs[reg]
                else:
                    self.regions[reg] = regs[reg]
            print(a,'-',b,' ', self.regions.__len__(), ':  ', self.regions)
            print('not found: ', not_found.__len__())



app = Gui()

app.mainloop()

# getOnlineData('C:/Users/Dmitry/PycharmProjects/untitled/venv/Scripts/Online')
# getData('All messages 17.02/')
