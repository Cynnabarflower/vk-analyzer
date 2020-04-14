from Gui.Widgets import *
import tkinter as tk
from tkinter import ttk
from Gui.Page import *
import Gui.Gui as Gui
import threading
import math
import json


class RegionalizePage(Page):
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
        self.scrollList = ScrollList(self, onclicked=lambda n: self.show_page(n), items=['MOS', 'SPB'], w=170,
                                     h=(20 + 10) * 10, item_height=20, bg=Gui.background_color, figurecolor='#91b0cf',
                                     fillcolor='#91b0cf', item_padding = 5, padding = 10)
        self.scrollList.grid(row=0, column=0, rowspan=2)
        self.regions_coordinates = json.load(open('allCoordinates.json', 'r'))
        for reg in self.regions_coordinates:
            for poly in reg['coordinates'][0]:
                for point in poly:
                    t = point[0]
                    point[0] = point[1]
                    point[1] = t
        c = tk.Canvas(self, width=360, height=245, bg='red', bd=-2)
        c.grid(column=1, row=0)
        self.canvas = c
        self.draw_map()

        self.button1 = ProgressButton(parent=self, text='Regionalize', onclicked=lambda: self.regionalize(), w=360,
                                      h=120)
        self.button1.grid(column=1, row=1)

    def draw_map(self, loop=True, draw_labels=False):
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

    def regionalize(self):
        self.regions = {}
        u_len = self.users.__len__()
        self.regionalizeProgress = [0, u_len]
        self.button1.watch_progress(self.regionalizeProgress)
        users_list = list(self.users.values())
        i = 0
        cities = json.load(open('citiesMap.json', 'r'))
        cities['1'] = {'region': 'RU-MOS'}
        cities['2'] = {'region': 'RU-LEN'}

        threads = []
        step = min(5000, round(u_len))
        while i < u_len:
            threads.append(
                Thread(target=self.__reg, args=([users_list, cities, i, min(u_len, i + step), i]), daemon=True))
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
            self.regionalizeProgress[0] += b - a
            print(a, '-', b, ' ', self.regions.__len__(), ':  ', self.regions)
            print('not found: ', not_found.__len__())
