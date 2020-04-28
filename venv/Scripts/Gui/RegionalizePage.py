from Gui.Widgets import *
import tkinter as tk
from tkinter import ttk
from Gui.Page import *
import Gui.Gui as Gui
import threading
import math
import json
from threading import Thread
from multiprocessing import Queue
import region_coordinates
import numpy as np
import pandas as pd


class RegionalizePage(Page):
    SCROLL_ITEM_HEIGHT = 25
    SCROLL_ITEM_WIDTH = 170
    SCROLL_ITEM_PADDING_X = 10
    SCROLL_ITEM_PADDING_Y = 7
    SCROLL_PADDING = (10, 20, 10, 20)
    SCROLL_WIDTH = SCROLL_ITEM_WIDTH + 2 * SCROLL_ITEM_PADDING_X
    SCROLL_HEIGHT = (SCROLL_ITEM_HEIGHT + SCROLL_ITEM_PADDING_Y) * 10
    WINDOW_WIDTH = 530
    WINDOW_HEIGHT = 360

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
        super().__init__(parent, controller)
        self.scrollList = ScrollList(self, onclicked=lambda n: self.show_page(n), w=self.SCROLL_WIDTH,
                                     h=340, item_height=self.SCROLL_ITEM_HEIGHT, bg=Gui.background_color,
                                     figurecolor='#91b0cf',
                                     fillcolor=None, item_padding=self.SCROLL_ITEM_PADDING_Y,
                                     padding=self.SCROLL_PADDING, progress_offset=5)
        self.scrollList.grid(row=0, column=0, rowspan=3, sticky='n')
        self.regions_coordinates = json.load(open('allCoordinates.json', 'r'))
        for reg in self.regions_coordinates:
            self.scrollList.add(reg['name'].replace('RU-', ''))
            for poly in reg['coordinates'][0]:
                for point in poly:
                    t = point[0]
                    point[0] = point[1]
                    point[1] = t
        self.scrollList.sort(reverse=False, key=lambda item: item.value)
        self.ruMap = RuMap(self, self.regions_coordinates, hower_callback = self.map_hower, )
        self.ruMap.grid(column=1, row=0, sticky = 's')

        self.row = row =  Row(self, align = 'n')
        row.grid(column = 1, row = 1, sticky='n')
        row.add(
            SimpleButton(parent=row, text='123', h = 50, w = 90),
            SimpleButton(parent=row, text='123', h = 50, w = 90),
        SimpleButton(parent=row, text='123', h = 50, w = 90),
        SimpleButton(parent=row, text='', h = 50, w = 90, icon=tk.PhotoImage(file='Gui/search.png'), fillcolor = '', loadcolor = '', onclicked = lambda: self.open_new()))

        self.button1 = ProgressButton(parent=self, text='Regionalize', onclicked=lambda: self.regionalize(), w=360,
                                      h=105, backgroundcolor = Gui.background_color)
        self.button1.grid(column=1, row=2)


    def open_new(self):
        app = tk.Tk()
        screen_width = math.floor(app.winfo_screenwidth() / 2)
        screen_height = math.floor(app.winfo_screenheight() / 2)
        app.geometry(str(screen_width)+'x'+str(screen_height))
        scaleX = screen_width/self.ruMap.width/1.1
        scaleY = screen_height/self.ruMap.height/1.1
        c = RuMap(app, coords=self.regions_coordinates, w = screen_width, h = screen_height, scaleX=min(scaleX, scaleY) * self.ruMap.scaleX)
        c.update_colors(self.regions, self.color_gradient)
        c.pack()
        app.mainloop()

    def resize(self, w, h, aw, ah):
        print('Regionalyzer resized')
        self.scale = (aw, ah)
        if w < self.scrollList.w + self.ruMap.width * aw:
            aw = (w - self.scrollList.w) / self.ruMap.width
        self.ruMap.resize(w, h, aw, ah)
        self.ruMap.update_colors(self.regions, self.color_gradient)
        self.scrollList.resize(w, h, 1, ah)
        self.row.resize(aw, ah)
        self.button1.resize(w, h, aw, ah)

    def map_hower(self, name):
        if name == '':
            self.scrollList.sort()
        else:
            self.scrollList.sort(update=False)
            self.scrollList.move(name=name.replace('RU-', ''), pos=0)
            self.scrollList.updatecanvas()

    def update_users(self, users):
        self.users = users

    def update_scrolllist(self, regions):
        if regions.__len__() > 0:
            for reg in regions:
                self.scrollList.setProgress(name=reg.replace('RU-', ''), progress=self.regions[reg] / self.ruMap.maxreg * 0.9,
                                            text=' ' + str(self.regions[reg]))
            self.scrollList.sort()

    def watch_progress(self):
        progress = self.regionalizeProgress[0] / self.regionalizeProgress[1]
        self.button1.drawProgress(progress)
        self.ruMap.update_colors(self.regions, self.color_gradient)
        self.update_scrolllist(self.regions)
        if progress < 1:
            self.after(500, self.watch_progress)

    def regionalize(self):
        self.regions = {}
        u_len = self.users.__len__()
        self.regionalizeProgress = [0, u_len]
        self.watch_progress()
        users_list = self.users
        i = 0
        cities = json.load(open('citiesMap.json', 'r'))
        cities['1'] = {'region': 'RU-MOS'}
        cities['2'] = {'region': 'RU-LEN'}

        threads = []
        step = min(50000, round(u_len))

        # while i < u_len:
        #     threads.append(
        #         Thread(target=self.__reg, args=([users_list, cities, i, min(u_len, i + step), i]), daemon=True))
        #     i += min(u_len, step)
        Thread(target=lambda: self._reg2(users_list, cities)).start()

        # for th in threads:
        #     th.start()

    def detect_region(self, user, cities, regs, not_found):
        if (not pd.isna(user['city'])):
            city_id = str(user['city']['id'])
            if city_id in cities:
                reg = cities[city_id]['region']
                if reg in regs:
                    regs[reg] += 1
                    return reg
                else:
                    regs[reg] = 1
                    return reg
            else:
                not_found[city_id] = ''
        return None


    def _reg2(self, users_df, cities):
        not_found = {}
        regs = {}
        users_df['detected_region'] = users_df.apply(lambda row: self.detect_region(row, cities, regs, not_found), axis = 1)
        with self.regions_lock:
            for reg in regs:
                if reg in self.regions:
                    self.regions[reg] += regs[reg]
                else:
                    self.regions[reg] = regs[reg]
            self.regionalizeProgress[0] += users_df.__len__()
            print(self.regions.__len__(), ':  ', self.regions)
            print('not found: ', not_found.__len__())

    def __reg(self, users_list, cities, a, b, name, ):
        not_found = {}
        regs = {}
        for i in range(a, b):
            if ('city' in users_list[i]):
                city_id = str(users_list[i]['city']['id'])
                if city_id in cities:
                    reg = cities[city_id]['region']
                    if reg in regs:
                        regs[reg] += 1
                    else:
                        regs[reg] = 1
                else:
                    not_found[city_id] = ''
        with self.regions_lock:
            for reg in regs:
                if reg in self.regions:
                    self.regions[reg] += regs[reg]
                else:
                    self.regions[reg] = regs[reg]
            self.regionalizeProgress[0] += b - a
            print(a, '-', b, ' ', self.regions.__len__(), ':  ', self.regions)
            print('not found: ', not_found.__len__())
