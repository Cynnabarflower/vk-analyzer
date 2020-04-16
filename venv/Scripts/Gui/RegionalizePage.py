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


class RegionalizePage(Page):

    SCROLL_ITEM_HEIGHT = 25
    SCROLL_ITEM_WIDTH = 170
    SCROLL_ITEM_PADDING_X = 10
    SCROLL_ITEM_PADDING_Y = 7
    SCROLL_PADDING = 20
    SCROLL_WIDTH = SCROLL_ITEM_WIDTH + 2 * SCROLL_ITEM_PADDING_X
    SCROLL_HEIGHT = (SCROLL_ITEM_HEIGHT + SCROLL_ITEM_PADDING_Y) * 10 + 2*SCROLL_PADDING
    WINDOW_WIDTH = 530
    WINDOW_HEIGHT = 350


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
                                     h=self.SCROLL_HEIGHT, item_height=self.SCROLL_ITEM_HEIGHT, bg=Gui.background_color, figurecolor='#91b0cf',
                                     fillcolor=None, item_padding = self.SCROLL_ITEM_PADDING_Y, padding = self.SCROLL_PADDING, progress_offset = 5)
        self.scrollList.grid(row=0, column=0, rowspan=2)
        self.regions_coordinates = json.load(open('allCoordinates.json', 'r'))
        for reg in self.regions_coordinates:
            self.scrollList.add(reg['name'].replace('RU-', ''))
            for poly in reg['coordinates'][0]:
                for point in poly:
                    t = point[0]
                    point[0] = point[1]
                    point[1] = t
        self.scrollList.sort(reverse=False, key=lambda item: item.value)
        c = tk.Canvas(self, width=360, height=245, bd=-2)
        c.grid(column=1, row=0)
        self.canvas = c
        self.draw_map()

        self.button1 = ProgressButton(parent=self, text='Regionalize', onclicked=lambda: self.regionalize(), w=360,
                                      h=105)
        self.button1.grid(column=1, row=1)

    def draw_map(self, loop=False, draw_labels=False):
        if self.controller.page_number == 1 or True:
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


            if regions.__len__() > 0:
                for reg in regions:
                    self.scrollList.setProgress(name = reg.replace('RU-', ''), progress=self.regions[reg]/maxreg * 0.9, text=' '+str(self.regions[reg]))
                self.scrollList.sort()


            for reg in coords:
                drawQuan = True
                for poly in reg['coordinates'][0]:
                    if reg['name'] in regions:
                        try:
                            regcolor = self.color_gradient[round((regions[reg['name']] - minreg) / (maxreg - minreg) * (
                                    self.color_gradient.__len__() - 1))]
                        except Exception as e:

                            print(minreg, ' ', maxreg, ' ', regions[reg['name']], ' ', round(
                                (regions[reg['name']] - minreg) / (maxreg - minreg) * (
                                        self.color_gradient.__len__() - 1)))

                    else:
                        regcolor = '#DDDDDD'
                    poly_coords = []
                    scaleX = 2
                    scaleY = scaleX * 5 / 3
                    offX = -15
                    offY = 85
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
                        poly_coords += [(offX + point[1]) * scaleX, (offY - point[0]) * scaleY]
                    c.create_polygon(poly_coords, fill=regcolor, outline='black')
                    if drawQuan and draw_labels:
                        c.create_text((polyminx + polymaxx) / 2, (polyminy + polymaxy) / 2,
                                      text=str(regions[reg['name']]) if reg['name'] in regions else '')
                        drawQuan = False
        if (loop):
            self.after(400, self.draw_map)

    def update_users(self, users):
        self.users = users

    def watch_progress(self):
        progress = self.regionalizeProgress[0] / self.regionalizeProgress[1]
        self.button1.drawProgress(progress)
        if progress < 1:
            self.draw_map(loop=False)
            self.after(500, self.watch_progress)


    def regionalize(self):
        self.regions = {}
        u_len = self.users.__len__()
        self.regionalizeProgress = [0, u_len]
        self.watch_progress()
        users_list = list(self.users.values())
        i = 0
        cities = json.load(open('citiesMap.json', 'r'))
        cities['1'] = {'region': 'RU-MOS'}
        cities['2'] = {'region': 'RU-LEN'}

        threads = []
        step = min(50000, round(u_len))
        q = Queue()
        while i < u_len:
            threads.append(
                Thread(target=self.__reg, args=([users_list, cities, i, min(u_len, i + step), i, q]), daemon=True))
            i += min(u_len, step)

        for th in threads:
            th.start()

    def __reg(self, users_list, cities, a, b, name,):
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
        with self.regions_lock:
            for reg in regs:
                if reg in self.regions:
                    self.regions[reg] += regs[reg]
                else:
                    self.regions[reg] = regs[reg]
            self.regionalizeProgress[0] += b - a
            print(a, '-', b, ' ', self.regions.__len__(), ':  ', self.regions)
            print('not found: ', not_found.__len__())
