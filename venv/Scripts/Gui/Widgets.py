import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math
import threading as th
from multiprocessing import Queue
import re
import time

BUTTON_WIDTH = 245
BUTTON_HEIGHT = 50
PADDING = 10

GRADIENT = [
    '#444444',
    '#555555',
    '#666666',
    '#777777',
    '#888888',
    '#999999',
]


class NavBar(tk.Frame):
    def __init__(self, parent, w=550, h=50, backgroundcolor='#4978a6', onclicked=(), pages=[], textcolor='#cadef7',
                 choosedcolor="#44ff44", borderradius=18, fillcolor='#224b79', padding=10, button_width=100):
        tk.Frame.__init__(self, parent)
        self.w = w
        self.h = h
        self.textcolor = textcolor
        self.backgroundcolor = backgroundcolor
        self.choosedcolor = fillcolor
        self.onclicked = onclicked
        self.pages = pages
        self.borderraadius = borderradius
        self.fillcolor = fillcolor
        self.currentPage = 0
        self.padding = padding
        self.button_width = button_width
        c = tk.Canvas(self, width=w, height=h, bg=backgroundcolor, bd=-2)
        c.bind("<Button-1>", self.clicked)
        c.pack(expand=True, fill=tk.X)
        self.canvas = c
        self.updatecanvas()

    def updatecanvas(self):
        # self.round_rectangle(self.padding, self.padding, self.w - self.padding, self.h - self.padding, radius=self.borderraadius,  outline=self.fillcolor, fill=self.fillcolor)
        x = self.padding
        self.buttons = []
        self.canvas.delete('all')

        for i in range(self.pages.__len__()):
            if self.currentPage == i:
                round_rectangle(self.canvas, x, self.padding, x + self.button_width, self.h - self.padding,
                                radius=self.borderraadius, outline=self.fillcolor, fill=self.fillcolor)
            self.canvas.create_text(x + self.button_width / 2, self.h / 2, text=str(self.pages[i]), fill=self.textcolor)
            self.buttons.append([x, x + self.button_width, self.pages[i]])
            x += (self.button_width + self.padding)

        self.update()

    def clicked(self, e):
        if (e.y > self.padding and e.y < self.w - self.padding):
            for i in range(self.buttons.__len__()):
                if (e.x >= self.buttons[i][0] and e.x <= self.buttons[i][1]):
                    self.currentPage = i
                    self.onclicked(i)
                    self.updatecanvas()
                    break


class ScrollList(tk.Frame):
    def __init__(self, parent, w=BUTTON_WIDTH + 2 * PADDING, h=(BUTTON_HEIGHT + PADDING) * 4 + PADDING / 2,
                 bg='#f1f0ec', onclicked=(), items=[], textcolor='#ffffff', figurecolor=None,
                 borderradius=18, fillcolor='#91b0cf', loadcolor='#224b79', choosable=False,
                 padding=(PADDING, PADDING, PADDING, PADDING), item_padding=PADDING,
                 item_height=BUTTON_HEIGHT, item_width=None, progress_offset=0, moved=None, pointerdown=None,
                 pointerup=None):
        tk.Frame.__init__(self, parent, bd=-2)
        self.w = w
        self.h = h
        self.nextTag = 0
        self.textcolor = textcolor
        self.backgroundcolor = bg
        self.onclicked = onclicked
        self.borderraadius = borderradius
        self.fillcolor = fillcolor
        self.loadcolor = loadcolor
        self.figurecolor = figurecolor
        self.choosable = choosable
        self.currentPage = 0
        self.progress_offset = progress_offset
        self.padding = (padding, padding, padding, padding) if isinstance(padding, int) or isinstance(padding,
                                                                                                      float) else (
            (padding[0], padding[1], padding[0], padding[1]) if padding.__len__() == 2 else padding)
        self.item_height = item_height
        self.item_width = item_width or self.w - self.padding[1] - self.padding[3]
        self.item_padding = item_padding
        self.scale = (1, 1)
        self.moved_buttons = {}
        c = tk.Canvas(self, width=w, height=h, bg=bg, bd=-2)
        c.bind("<Button-1>", self.pointerdown if pointerdown is None else pointerdown)
        c.bind("<B1-Motion>", self.moved if moved is None else moved)
        c.bind("<MouseWheel>", self.moved if moved is None else moved)
        c.bind("<ButtonRelease-1>", self.pointerup if pointerup is None else pointerup)
        self.canvas = c
        self.update_time = 0
        self.dy = 0
        self.items = []
        self.buttons = []
        for item in items:
            self.add(item)
        c.pack()
        self.initcanvas()
        self.updatecanvas()

    def add(self, element, update=True):
        self.buttons.append(
            self.ScrollListButton('item' + str(self.nextTag), y=0, value=element, fillcolor=self.fillcolor,
                                  choosable=self.choosable)
        )
        self.nextTag += 1
        canvas = tk.Canvas(self)
        text = canvas.create_text(100, 100, text=element, font=(self.buttons[-1].font, self.buttons[-1].fontsize))
        box = canvas.bbox(text)
        while (box[2] - box[0] > self.item_width - 2 or box[3] - box[
            1] > self.item_height - 2):
            self.buttons[-1].fontsize -= 1
            text = canvas.create_text(100, 100, text=element,
                                      font=(self.buttons[-1].font, self.buttons[-1].fontsize))
            box = canvas.bbox(text)
        self.visibleheight = min(
            self.h - self.buttons.__len__() * (self.item_height + self.item_padding) - self.padding[0] - self.padding[
                2],
            0)
        # self.moved_buttons[self.buttons[-1]] = self.buttons.__len__()-1
        if update:
            self.updatecanvas()

    def remove(self, i=-1, button=None, name='', stage=1):
        # print('removing  ', button.text)
        if i > -1:
            if stage == 0:
                self.remove_animation(self.buttons[i])
            else:
                self.canvas.delete(self.buttons[i].tag)
                self.canvas.delete(self.buttons[i].tag + 'text')
                self.canvas.delete(self.buttons[i].tag + 'progress')
                self.buttons.remove(i)
        elif button != None:
            if stage == 0:
                self.remove_animation(button)
            else:
                self.canvas.delete(button.tag)
                self.canvas.delete(button.tag + 'text')
                self.canvas.delete(button.tag + 'progress')
                self.buttons.remove(button)
        else:
            for button in self.buttons:
                if button.value == name:
                    if stage == 0:
                        self.remove_animation(button)
                    else:
                        self.canvas.delete(button.tag)
                        self.canvas.delete(button.tag + 'text')
                        self.canvas.delete(button.tag + 'progress')
                        self.buttons.remove(button)
                    break
        self.updatecanvas()

    def reset(self):
        for button in self.buttons:
            self.canvas.delete(button.tag)
            self.canvas.delete(button.tag + 'text')
            self.canvas.delete(button.tag + 'progress')
        self.buttons.clear()
        self.updatecanvas()

    def remove_animation(self, button, stage=0):
        button.progress = 0
        self.remove(button=button)

    def resize(self, w, h, aw, ah):
        self.canvas.configure(width=self.w * aw, height=self.h * ah)
        self.scale = (aw, ah)
        print(w, h, aw, ah, 'self: ', self.h * ah)
        self.canvas.delete('all')
        self.initcanvas()
        # self.updatecanvas()

    def initcanvas(self):
        if self.figurecolor is not None:
            round_rectangle(self.canvas, self.padding[3], self.padding[0], self.w * self.scale[0] - self.padding[1],
                            (self.h * self.scale[1]) - self.padding[2], radius=32, fill=self.figurecolor)
        y = self.dy + self.item_padding + self.padding[0]
        for button in self.buttons:
            self.draw_new(button, y)
            y += (self.item_height + self.item_padding)
        self.canvas.create_rectangle(self.padding[3], 0, self.w * self.scale[0] - self.padding[1], self.padding[0],
                                     outline=self.backgroundcolor,
                                     fill=self.backgroundcolor, tag='frame')
        self.canvas.create_rectangle(self.padding[3], self.h * self.scale[1] - self.padding[2],
                                     self.w * self.scale[0] - self.padding[1],
                                     self.h * self.scale[1], outline=self.backgroundcolor,
                                     fill=self.backgroundcolor, tag='frame')

    def update_button(self, button, y):
        if not button.needsupdate:
            if y != button.y:
                self.canvas.move(button.tag, 0, y - button.y)
                progress = self.canvas.find_withtag(button.tag + 'progress')
                self.canvas.move(progress, 0, y - button.y)
                text = self.canvas.find_withtag(button.tag + 'text')
                self.canvas.move(text, 0, y - button.y)
                # self.canvas.itemconfigure(text, text = str(button.y)+'->'+str(y)+" "+button.text)
                button.set_y(y)
        else:
            self.canvas.delete(button.tag)
            self.canvas.delete(button.tag + 'text')
            self.canvas.delete(button.tag + 'progress')
            self.draw_new(button, y)

    def getVisibleIndexes(self):
        block_height = (self.item_height + self.item_padding)
        y = self.dy + self.item_padding + self.padding[0]
        b = max(math.floor(-y / block_height), 0)
        e = min(b + math.floor(self.h * self.scale[1] / block_height) + 2, self.buttons.__len__())
        return (b, e)

    def updatecanvas(self, need_check = True):
        # print('Scrollbox update..')
        # if self.update_time < 0:
        #     return
        # delta = time.time() - self.update_time
        # if (need_check and delta < 0.005):
        #     print(delta)
        #     self.update_time = -1
        #     self.after(100, lambda: self.updatecanvas(need_check = False))
        #     return

        self.update_time = time.time()
        update_next = {}
        block_height = (self.item_height + self.item_padding)
        y = self.dy + self.item_padding + self.padding[0]
        b, e = self.getVisibleIndexes()
        for i in range(b, e, 1):
            self.update_button(self.buttons[i], y + i * block_height)
            update_next[self.buttons[i]] = i
            if self.buttons[i] in self.moved_buttons:
                del self.moved_buttons[self.buttons[i]]

        for button, k in self.moved_buttons.items():
            self.update_button(button, y + k * block_height)

        self.moved_buttons = update_next
        self.canvas.tag_raise('frame')
        self.update()
        return

        for button in self.buttons:
            if (button.y < self.padding[0] or button.y > self.h * self.scale[1]) and (
                    button.old_y < self.padding[0] or button.old_y > self.h * self.scale[1]):
                continue
            if y > self.h * self.scale[1] and button.y:
                print("----%.2f---- updating moved" % (time.time() - st))
                st = time.time()
                for button, k in self.moved_buttons.items():
                    self.update_button(button, self.dy + self.item_padding + self.padding[0] + k * (
                            self.item_height + self.item_padding))
                print("----%.2f done" % (time.time() - st))
                break
            if button in self.moved_buttons:
                del self.moved_buttons[button]
            self.update_button(button, y)
            # for particle in self.buttons[i]['particles']:
            #     self.canvas.create_rectangle(particle[0], particle[1], particle[2], particle[3], fill=self.backgroundcolor, outline=self.backgroundcolor)
            y += (self.item_height + self.item_padding)
        self.canvas.tag_raise('frame')
        self.update()

    def draw_new(self, button, y):

        x0 = self.padding[3] + (
                self.w * self.scale[0] - self.padding[1] - self.padding[3] - self.item_width * self.scale[0]) / 2
        x1 = x0 + self.item_width * self.scale[0]
        if self.fillcolor is not None:
            round_rectangle(self.canvas, x0, y, x1, y + self.item_height,
                            radius=self.borderraadius, outline=button.fillcolor,
                            fill=button.fillcolor, tag=button.tag)
        if button.isChosen:
            round_rectangle(self.canvas, x0, y, x1, y + self.item_height,
                            radius=self.borderraadius, outline=self.loadcolor,
                            fill=self.loadcolor, tag=button.tag)

        if button.progress > 0.02:
            round_rectangle(self.canvas, x0 + self.progress_offset * self.scale[0], y,
                            ((self.item_width - self.progress_offset) * button.progress + self.progress_offset) *
                            self.scale[0] + x0,
                            y + self.item_height,
                            radius=self.borderraadius, outline=self.loadcolor, fill=self.loadcolor,
                            tag=button.tag + 'progress')
        elif button.progress > 0:
            self.canvas.create_rectangle(x0 + self.progress_offset, y, ((
                                                                                self.item_width - self.progress_offset) * button.progress + self.progress_offset) *
                                         self.scale[0] + x0,
                                         y + self.item_height, outline=self.loadcolor, fill=self.loadcolor,
                                         tag=button.tag + 'progress')
        self.canvas.create_text((x1 + x0) / 2, y + self.item_height / 2, text=str(button.text),
                                fill=self.textcolor,
                                font=(button.font, button.fontsize),
                                tag=button.tag + 'text')
        button.set_y(y)
        button.needsupdate = False

    def sort(self, key=lambda item: item.progress, reverse=True, update=True):
        b, e = self.getVisibleIndexes()
        for i in range(b, e, 1):
            self.buttons[i].needsupdate = True
            self.canvas.delete(self.buttons[i].tag)
            self.canvas.delete(self.buttons[i].tag + 'text')
            self.canvas.delete(self.buttons[i].tag + 'progress')
        self.buttons = sorted(self.buttons, key=key, reverse=reverse)
        self.dy = 0

        b, e = self.getVisibleIndexes()
        self.moved_buttons = {self.buttons[i]: i for i in range(b, e, 1)}
        if update:
            self.updatecanvas()

    def move(self, name, pos=None, up=False, down=False):
        for i in range(self.buttons.__len__()):
            if self.buttons[i].value == name:
                item = self.buttons[i]
                if pos is not None:
                    del self.buttons[i]
                    self.buttons.insert(pos, item)
                    self.moved_buttons[item] = pos
                    return
                if up:
                    self.buttons.remove(item)
                    self.buttons.insert(i - 1, item)
                    self.moved_buttons[item] = i - 1
                    return
                if down:
                    self.buttons.remove(item)
                    if self.buttons.__len__() > i + 1:
                        self.buttons.insert(i + 1, item)
                        self.moved_buttons[item] = i + 1
                    else:
                        self.buttons.append(item)
                        self.moved_buttons[item] = self.buttons.__len__() - 1
                    return

    def chosen(self, e, i):
        if self.buttons[i].choosable:
            self.buttons[i].chosen()
        if self.onclicked:
            self.onclicked(self.buttons[i])

    def pointerup(self, e, update=True):
        if ((e.x - self.pointerx) == 0 and (
                e.y - self.pointery) == 0 and e.y > self.padding[0] and e.y < self.h * self.scale[1] - self.padding[2]):
            if self.choosable:
                for i in range(self.buttons.__len__()):
                    if (e.y >= self.buttons[i].y and e.y <= self.buttons[i].y + self.item_height):
                        self.chosen(e, i)
                        break
            else:
                return

        if self.dy == self.padding[0] + self.item_padding:
            self.dy = 0
            if update:
                self.updatecanvas()
        elif self.dy == self.visibleheight - self.padding[2]:
            self.dy = self.visibleheight
            if update:
                self.updatecanvas()

        # self.lasty = 0
        # self.pointerx = 0
        # self.pointery = 0
        # self.updatecanvas()

    def pointerdown(self, e):
        print('Scrollbox down')
        self.pointerx = e.x
        self.pointery = e.y
        self.lasty = e.y

    def moved(self, d, update=True):

        ndy = d.y - self.lasty if d.delta == 0 else self.item_height * d.delta/100

        self.dy = self.dy + ndy
        # print(ndy, '  ', self.dy + ndy, '  ',
        #       min(self.padding / 2, self.dy + ndy) if ndy > 0 else max(self.dy + ndy, self.visibleheight), '  ',
        #       self.buttons[0].y, '   ', self.visibleheight)
        self.dy = min(self.padding[2] + self.item_padding, self.dy + ndy) if ndy > 0 else max(self.dy + ndy,
                                                                                              self.visibleheight -
                                                                                              self.padding[0])
        print('Scrollbox moved')
        if update:
            self.updatecanvas()
        self.lasty = d.y

    def setProgress(self, i=-1, name='', progress=0, text=''):
        if i > -1:
            self.buttons[i].set_progress(progress)
            if text is not None:
                self.buttons[i].set_text(self.buttons[i].value + text)

        else:
            for button in self.buttons:
                if button.text == name:
                    button.set_progress(progress)
                    if text is not None:
                        button.set_text(button.value + text)
                    break
        self.updatecanvas()

    class ScrollListButton:
        def __init__(self, tag, y, value=None, text=None, font='Colibri', fontsize=25, progress=0, fillcolor='#ffffff',
                     choosable=False):
            self.tag = tag
            self.y = y
            self.old_y = y
            self.value = value or text
            self.text = text or str(value)
            self.font = font
            self.fontsize = fontsize
            self.progress = progress
            self.progresstext = ''
            self.fillcolor = fillcolor
            self.needsupdate = True
            self.isChosen = False
            self.choosable = choosable

        def chosen(self, chosen=None):
            if (chosen == None or chosen != self.isChosen):
                self.isChosen = not self.isChosen
                self.needsupdate = True

        def set_text(self, text):
            self.text = text
            self.needsupdate = True

        def set_progress(self, progress):
            self.progress = progress
            self.needsupdate = True

        def set_y(self, y):
            self.old_y = self.y
            self.y = y


class ProgressButton(tk.Frame):

    def __init__(self, parent, w=BUTTON_WIDTH + 2 * PADDING, h=BUTTON_HEIGHT + 2 * PADDING, backgroundcolor='#f1f0ec',
                 onclicked=None, text='+', textcolor='#ffffff',
                 fillcolor="#4978a6", loadcolor='#224b79', borderradius=18, padding=10, font=("Colibri", 25)):
        tk.Frame.__init__(self, parent)
        self.w = w
        self.h = h
        self.text = text
        self.font = font
        self.textcolor = textcolor
        self.backgroundcolor = backgroundcolor
        self.fillcolor = fillcolor
        self.loadcolor = loadcolor
        self.onclicked = onclicked
        self.borderradius = borderradius
        self.padding = padding
        self.scale = (1, 1)
        c = tk.Canvas(self, width=w, height=h, bg=backgroundcolor)
        c.bind("<Button-1>", self.clicked)
        c.pack()
        self.canvas = c
        self.updatecanvas()

    def fit_text(self):
        canvas = tk.Canvas(self)
        text = canvas.create_text(100, 100, text=self.text, font=self.font)
        box = canvas.bbox(text)
        while (box[2] - box[0] > (self.w - self.padding) * 0.8 * self.scale[0] - 2 or (box[3] - box[1]) > (
                self.h - self.padding) * 0.8 * self.scale[1] - 2):
            self.font = (self.font[0], self.font[1] - 1)
            text = canvas.create_text(100, 100, text=self.text,
                                      font=self.font)
            box = canvas.bbox(text)
        while ((box[2] - box[0] < (self.w - self.padding) * 0.8 * self.scale[0] and box[3] - box[1] < (
                self.h - self.padding) * 0.8 * self.scale[1]) and self.font[1] < 30):
            self.font = (self.font[0], self.font[1] + 1)
            text = canvas.create_text(100, 100, text=self.text,
                                      font=self.font)
            box = canvas.bbox(text)

    def resize(self, w, h, aw, ah):
        self.scale = (aw, ah)
        self.canvas.configure(height=self.h * ah, width=self.w * aw)
        self.fit_text()
        self.canvas.delete('all')
        self.updatecanvas()

    def clicked(self, e):
        gen = self.onclicked()
        if gen:
            i = 100
            for i in gen:
                print(i)
                self.drawProgress(i)
                self.update()
            if i < 100:
                self.drawProgress(100)

    def updatecanvas(self):
        self.canvas.delete('text')
        self.canvas.delete('progress')
        round_rectangle(self.canvas, self.padding * self.scale[0], self.padding * self.scale[1],
                        (self.w - self.padding) * self.scale[0], (self.h - self.padding) * self.scale[1],
                        radius=self.borderradius * self.scale[0], outline=self.fillcolor, fill=self.fillcolor)
        # self.canvas.create_rectangle(0, 0, prorgess / 100 * self.w, self.h, outline=self.backgroundcolor, fill=self.backgroundcolor)
        self.canvas.create_text(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2, text=self.text,
                                fill=self.textcolor, font=self.font, tag='text')

    def drawProgress(self, prorgess):
        self.canvas.delete('text')
        self.canvas.delete('progress')
        if prorgess > 0:
            round_rectangle(self.canvas, self.padding * self.scale[0], self.padding * self.scale[1],
                            ((self.w - self.padding * 2) * prorgess + self.padding) * self.scale[0],
                            (self.h - self.padding) * self.scale[1],
                            radius=self.borderradius * self.scale[0], outline=self.loadcolor, fill=self.loadcolor,
                            tag='progress')
        if prorgess < 1:
            self.canvas.create_text(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2,
                                    text=str(math.floor(prorgess * 100)) + '%',
                                    fill=self.textcolor,
                                    tag='text', font=self.font)
        else:
            self.canvas.create_text(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2, text=str('done!'),
                                    fill=self.textcolor, tag='text',
                                    font=self.font)
            self.after(1000, self.updatecanvas)
        self.update()

    def watch_progress(self, progress):
        if progress.__len__() == 2:
            self.drawProgress(progress[0] / progress[1])
        if progress[0] / progress[1] < 1:
            self.after(500, lambda: self.watch_progress(progress))


class ProgressBar:
    def __init__(self, controller, canvas, x, y, r1, r2, color1, color2, font=('Colibri', 28)):
        self.canvas = canvas
        self.controller = controller
        self.x = x
        self.y = y
        self.r1 = r1
        self.r2 = r2
        self.color1 = color1
        self.font = font
        self.color2 = color2
        self.points1 = ProgressBar.getcircle(x, y, r1, r2, progress_from=0, progress_to=1, width=6.283 / 360,
                                             step=6.283 / 360)
        self.id = str(id(self))
        self.progress = 0.75
        self.time = 0
        self.working = True
        self.scale = (1, 1)
        self.fit_text()
        for point in self.points1:
            canvas.create_polygon(point, fill=color1, smooth=True, tag='outer_' + self.id)
        self.canvas.create_polygon(ProgressBar.getcircle(x, y, r1, r2, 0), fill=self.color2, smooth=False,
                                   tag='inner_' + self.id)
        self.canvas.create_text(x, y, text='0', font=self.font, fill=color2, tag='progress_' + self.id)

    def fit_text(self):
        canvas = tk.Canvas()
        text = canvas.create_text(100, 100, text='100', font=self.font)
        box = canvas.bbox(text)
        while (box[2] - box[0] > (self.r1 * 2) * 0.9 * self.scale[0] - 1 or (box[3] - box[1]) > (
                self.r1 * 2) * 0.9 * self.scale[1] - 1):
            self.font = (self.font[0], self.font[1] - 1)
            text = canvas.create_text(100, 100, text='100',
                                      font=self.font)
            box = canvas.bbox(text)
        while ((box[2] - box[0] < (self.r1 * 2) * 0.9 * self.scale[0] and box[3] - box[1] < (
                self.r1 * 2) * 0.9 * self.scale[1]) and self.font[1] < 30):
            self.font = (self.font[0], self.font[1] + 1)
            text = canvas.create_text(100, 100, text='100',
                                      font=self.font)
            box = canvas.bbox(text)

    def drawprogress(self, progress=-1):
        if not self.working:
            self.canvas.delete('inner_' + self.id)
            self.canvas.itemconfigure('outer_' + self.id, state='hidden')
            self.working = True
            return
        self.canvas.itemconfigure('outer_' + self.id, state='normal')
        self.canvas.lift('outer_' + self.id)
        if progress >= 0:
            self.canvas.delete('inner_' + self.id)
            self.canvas.create_polygon(ProgressBar.getcircle(self.x, self.y, r1, r2, progress_to=progress),
                                       fill=self.color2, smooth=True, tag='inner_' + self.id)
            self.canvas.itemconfigure('progress_' + self.id, text=str(math.floor(progress * 100)))
        else:
            self.canvas.delete('inner_' + self.id)
            to = (self.progress + 0.1) / 5
            for point in ProgressBar.getcircle(self.x, self.y, self.r1, self.r2, progress_from=self.progress / 5,
                                               progress_to=to, width=0.1, step=0.1):
                self.canvas.create_polygon(point, fill=self.color2, smooth=False,
                                           tag='inner_' + self.id)
            self.canvas.itemconfigure('progress_' + self.id, text=str(math.floor(self.time)))
            self.progress = (self.progress + 0.1) % 10
            self.time += 0.1
            self.controller.after(100, self.drawprogress)

    @staticmethod
    def getcircle(x, y, r1, r2, progress_from=0, progress_to=1, width=0.0875, step=0.0875):
        t = min(progress_from, progress_to) * 6.283
        progress_to = max(progress_to, progress_from)
        points = []
        # step = 0.01745 # 1 deg
        # step = 0.0875  # 5 deg
        # step = 0.1745  # 10 deg
        # step = 0.349     # 20 deg
        while t < 6.283 * progress_to:
            cos = math.cos(t - width)
            sin = math.sin(t - width)
            x1 = (x + r1 * cos)
            y1 = (y + r1 * sin)
            cos2 = math.cos(t + width)
            sin2 = math.sin(t + width)
            x2 = (x + r2 * cos)
            y2 = (y + r2 * sin)
            x4 = (x + r1 * cos2)
            y4 = (y + r1 * sin2)
            x3 = (x + r2 * cos2)
            y3 = (y + r2 * sin2)
            points.append([
                x1, y1,
                # (x1+x2)/2, (y1 + y2)/2,
                x2, y2,
                # (x2 + x3) / 2, (y2 + y3) / 2,
                x3, y3,
                # (x3 + x4) / 2, (y3 + y4) / 2,
                x4, y4,
                # (x1 + x4) / 2, (y1 + y4) / 2,
            ])
            t += step

        return points


class SimpleButton(tk.Frame):

    def __init__(self, parent, w=BUTTON_WIDTH + 2 * PADDING, h=BUTTON_HEIGHT + 2 * PADDING, backgroundcolor='#f1f0ec',
                 onclicked=None, text='', icon=None, textcolor='#ffffff',
                 fillcolor="#4978a6", loadcolor='#224b79', borderradius=18, padding=10, font=("Colibri", 25),
                 fixed=False):
        tk.Frame.__init__(self, parent, highlightthickness = 0)
        self.w = w
        self.h = h
        self.scale = (1, 1)
        self.text = text
        self.font = font
        self.textcolor = textcolor
        self.backgroundcolor = backgroundcolor
        self.fillcolor = fillcolor
        self.loadcolor = loadcolor
        self.onclicked = onclicked
        self.borderradius = borderradius
        self.padding = padding
        self.fixed = fixed
        self.state = False
        self.icon = icon
        self.rotation = [0, 0, 0]
        c = tk.Canvas(self, width=w, height=h, bg=self.backgroundcolor, bd=-2)
        c.bind("<Button-1>", self.clicked)
        c.pack()
        self.canvas = c
        self.fit_text()
        self.updatecanvas(self.fillcolor)

    def set_text(self, text):
        self.text = text
        self.font = fit_text((self.w - self.padding * 2) * self.scale[0] * 0.8, (self.h - self.padding * 2) * self.scale[1] * 0.8, self.text, self.font)

    def fit_text(self):
        canvas = tk.Canvas(self)
        text = canvas.create_text(100, 100, text=self.text, font=self.font)
        box = canvas.bbox(text)
        while (box[2] - box[0] > (self.w - self.padding) * 0.8 * self.scale[0] - 2 or (box[3] - box[1]) > (
                self.h - self.padding) * 0.8 * self.scale[1] - 2):
            self.font = (self.font[0], self.font[1] - 1)
            text = canvas.create_text(100, 100, text=self.text,
                                      font=self.font)
            box = canvas.bbox(text)
        while ((box[2] - box[0] < (self.w - self.padding) * 0.8 * self.scale[0] and box[3] - box[1] < (
                self.h - self.padding) * 0.8 * self.scale[1]) and self.font[1] < 30):
            self.font = (self.font[0], self.font[1] + 1)
            text = canvas.create_text(100, 100, text=self.text,
                                      font=self.font)
            box = canvas.bbox(text)

    def rotate(self, ox = 0, oy = 0, oz = 0):
        self.rotation = [ox, oy, oz]
        self.updatecanvas(self.fillcolor)

    def resize(self, w, h):
        self.scale = (w, h)
        self.canvas.configure(height=self.h * h, width=self.w * w)
        self.fit_text()
        self.updatecanvas(self.fillcolor)

    def clicked(self, e):
        if self.fixed:
            self.updatecanvas(self.loadcolor if not self.state else self.fillcolor)
            self.state = not self.state
            if self.onclicked is not None:
                self.onclicked(self.state)
            self.updatecanvas(self.loadcolor if not self.state else self.fillcolor)
        else:
            self.updatecanvas(self.loadcolor)
            if self.onclicked is not None:
                self.onclicked()
            self.updatecanvas(self.fillcolor)

    def updatecanvas(self, color=None):
        self.canvas.delete('all')
        color = self.fillcolor if color is None else color
        rrp = round_rectangle_points(self.padding * self.scale[0], self.padding * self.scale[1],
                        (self.w - self.padding) * self.scale[0], (self.h - self.padding) * self.scale[1], radius=self.borderradius)
        rotate_polygon(rrp, self.w * self.scale[0] / 2, self.h/2 * self.scale[1], ox = self.rotation[0], oy = self.rotation[1], oz = self.rotation[2])
        self.canvas.create_polygon(rrp, outline=color, fill=color, smooth = True)
        # round_rectangle(self.canvas, self.padding * self.scale[0], self.padding * self.scale[1],
        #                 (self.w - self.padding) * self.scale[0], (self.h - self.padding) * self.scale[1],
        #                 radius=self.borderradius, outline=color, fill=color)
        if self.icon is not None:
            if self.text == '':
                self.canvas.create_image(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2, image=self.icon,
                                         anchor='center')
            else:
                self.canvas.create_image(self.w * self.scale[0] / 5, self.h * self.scale[1] / 2, image=self.icon,
                                         anchor='center')
        self.canvas.create_text(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2, text=self.text,
                                fill=self.textcolor, font=self.font)


def round_rectangle(canvas, x1, y1, x2, y2, radius=25, radius1=None, radius2=None, radius3=None, radius4=None,
                    **kwargs):
    points = round_rectangle_points(x1, y1, x2, y2, radius, radius1, radius2, radius3, radius4)
    return canvas.create_polygon(points, **kwargs, smooth=True)


def round_rectangle_points(x1, y1, x2, y2, radius=25, radius1=None, radius2=None, radius3=None, radius4=None):
    if radius * 2 > (x2 - x1):
        radius = (x2 - x1 - 2) / 2

    radius1 = radius1 or radius
    radius2 = radius2 or radius
    radius3 = radius3 or radius
    radius4 = radius4 or radius

    points = [x1 + radius1, y1,
              # x1 + radius, y1,
              # x2 - radius, y1,
              x2 - radius2, y1,
              x2, y1,
              x2, y1 + radius2,
              # x2, y1 + radius,
              # x2, y2 - radius,
              x2, y2 - radius3,
              x2, y2,
              x2 - radius3, y2,
              # x2 - radius, y2,
              # x1 + radius, y2,
              x1 + radius4, y2,
              x1, y2,
              x1, y2 - radius4,
              # x1, y2 - radius,
              # x1, y1 + radius,
              x1, y1 + radius1,
              x1, y1]
    return points


def round_corner_points(x, y, w, h, radius=25):
    points = [
        x, y,
        x, y,
        x, y + h,
        x, y + radius,
           x + radius, y,
           x + w, y,
        x, y,
    ]
    return points


def round_frame_points(x, y, w, h, radius=25):
    corners = []
    for i in range(4):
        points = round_corner_points(x - w / 2, y - h / 2, w / 2, h / 2, radius=radius)
        rotate_polygon(points, x, y, oz=i * -math.pi / 2)
        corners.append(points)
    return corners


class InputField(tk.Frame):
    def __init__(self, controller, canvas, x, y, w, h, text='', empty_text='', on_enter=None, bg='#ffffff',
                 font=('Colibri', 26), maxlen=-1, is_password=False):
        tk.Frame.__init__(self, controller, highlightthickness=0)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.bg = bg
        self.maxlen = maxlen
        self.empty_text = empty_text
        self.on_ener = on_enter
        self.font = font
        self.canvas = canvas
        self.text = text
        self.visible_text = ''
        self.id = 'inputField_' + str(id(self))
        self.scale = (1, 1)
        self.in_focus = False
        self.canvastext = None
        self.canvasbg = None
        self.controller = controller
        self.text_padding = 8
        self.is_password = is_password
        self.coursor = -1

        if canvas is None:
            self.canvas = tk.Canvas(self, width=self.w, height=self.h, bg=self.bg, bd=-2, highlightthickness = 0)
            self.canvas.bind("<Button-1>", self.clicked)
            self.x = 0
            self.y = 0
            self.canvas.pack()


    def hide(self):
        self.canvas.delete(self.id)
        self.canvas.delete(self.id + '_text')

    def init_canvas(self):
        self.canvas.delete(self.id)
        self.canvas.delete(self.id + '_text')
        self.visible_text = self.text if not self.is_password else ('*' * self.text.__len__())
        self.canvasbg = self.canvas.create_polygon(
            round_rectangle_points(self.x * self.scale[0], self.y * self.scale[1], (self.x + self.w) * self.scale[0],
                                   (self.y + self.h) * self.scale[1]), smooth=True, fill=self.bg, tag=self.id)
        self.canvastext = self.canvas.create_text((self.x + self.text_padding) * self.scale[0],
                                                  (self.y + self.h / 2) * self.scale[1], text=self.visible_text,
                                                  anchor='w', tag=self.id + '_text',
                                                  font=self.font)
        self.update_text()

    def key(self, e):
        if self.in_focus:
            if e.keycode == 8:
                self.text = self.text[:-1]
                self.coursor = max(-1, self.coursor - 1)
                self.update_text()
            elif e.keycode == 37:
                self.coursor = max(-1, self.coursor - 1)
            elif e.keycode == 39:
                self.coursor = min(self.text.__len__(), self.coursor + 1)
            elif e.char == '\t' or e.char == '\n' or e.char == '\r' or e.char == '':
                self.in_focus = False
                if self.on_ener:
                    self.on_ener(self)
                self.update_text()
            elif self.maxlen < 0 or self.text.__len__() < self.maxlen:
                if e.char != '':
                    self.text += e.char
                    self.coursor = min(self.text.__len__(), self.coursor + 1)
                    self.update_text()

    def clicked(self, e):
        elems = self.canvas.find_overlapping(e.x, e.y, e.x, e.y)
        if self.canvasbg in elems or self.canvastext in elems:
            self.in_focus = True
            for i in range(10):
                self.canvas.bind(i, self.key)
            self.canvas.bind('<Key>', self.key)
            self.canvas.focus_set()
            self.blink()
            return True
        else:
            self.in_focus = False
            return False

    def blink(self, t=False):
        if self.in_focus:
            if self.focus_lastfor() != self.canvas:
                self.in_focus = False
                self.update_text()
                return
            if t:
                self.visible_text = (self.text if not self.is_password else ('*' * self.text.__len__())) + '│'
                # self.visible_text = self.visible_text[:self.coursor] +'│'+ self.visible_text[self.coursor:]
            else:
                self.visible_text = self.text if not self.is_password else ('*' * self.text.__len__())
            self.canvas.itemconfigure(self.id + '_text', text=self.visible_text, font=self.font)
            self.controller.after(500, lambda: self.blink(t=not t))
        elif not t:
            self.update_text()

    def update_text(self):
        fill = '#224b79'
        if self.text == '':
            fill = '#91b0cf'
            self.visible_text = self.empty_text
        else:
            self.visible_text = self.text if not self.is_password else ('*' * self.text.__len__())

        self.font = fit_text((self.w - self.text_padding * 2) * self.scale[0], (self.h - 4) * self.scale[1],
                             self.visible_text + ' ' if self.maxlen < 0 else (
                                     self.visible_text + ' ' * (1 + self.maxlen - self.text.__len__())), self.font)

        self.canvas.itemconfigure(self.id + '_text', text=self.visible_text, font=self.font, fill=fill)

    def resize(self, w, h, aw, ah):
        self.scale = (aw, ah)
        self.init_canvas()


class Row(tk.Frame):
    def __init__(self, parent, align):
        tk.Frame.__init__(self, parent)
        self.widgets = []
        self.align = align

    def add(self, *widgets):
        for widget in widgets:
            widget.grid(column=self.widgets.__len__(), row=0, sticky='n')
            self.widgets.append(widget)

    def resize(self, w, h):
        for widget in self.widgets:
            widget.resize(w, h)


class RotatingCard(tk.Frame):
    def __init__(self, parent, w=265, h=265, padding=10, bg='#f1f0ec', view=None, init=None, clicked=None):
        tk.Frame.__init__(self, parent)
        self.w = w
        self.h = h
        self.padding = padding
        self.userscanvas = canvas = tk.Canvas(self, width=self.w, height=self.h, bg=bg, highlightthickness=0)
        self.userscanvas.pack(anchor='n')
        self.userscanvas.bind("<Button-1>", self.tapped)
        self.scale = (1, 1)
        self.a = 0
        self.view = view
        self.clicked = clicked
        self.bg = bg

        if init:
            init(canvas, self.w, self.h, self.padding, self.scale)

        self.rotate(0)
        # canvas.create_image(265 / 2, (265 - 2 * padding) * 40 / 100 + padding, image=self.image, anchor='center')
        # for coords in self.image_coords:
        #     canvas.create_polygon(coords, fill='#ffffff', smooth=True, tag='img')

    def add(self, *widgets):
        for widget in widgets:
            widget.grid(column=self.widgets.__len__(), row=0, sticky='n')
            self.widgets.append(widget)

    def resize(self, w, h, aw, ah):
        self.userscanvas.configure(height=self.h * ah, width=self.w * aw)
        self.scale = (aw, ah)
        self.rotate(self.a)
        # self.userscanvas.configure(width=aw * 285, height=ah * 265)
        # current_scale = (aw / self.last_scale[0], ah / self.last_scale[1])
        # self.userscanvas.scale('all', 0, 0, current_scale[0], current_scale[1])
        # self.last_scale = (aw, ah)

    def tapped(self, e):
        change_page = False
        if self.a == 0:
            if (self.w * 0.85 - self.padding) * self.scale[0] <= e.x <= (self.w * 0.95 - self.padding) * self.scale[0]:
                if (self.h / 10) * self.scale[1] < e.y < (self.h / 6 + 24) * self.scale[1]:
                    change_page = True
                    self.rotate(180)
        else:
            if (self.w - (self.w * 0.95 - self.padding)) * self.scale[0] <= e.x <= (
                    self.w - (self.w * 0.85 - self.padding)) * self.scale[0]:
                if (self.h / 10) * self.scale[1] < e.y < (self.h / 6 + 24) * self.scale[1]:
                    change_page = True
                    self.rotate(0)
        if not change_page and self.clicked:
            self.clicked(e, self.userscanvas,  self.w, self.h, self.padding, self.scale, (self.a % 360) * math.pi / 180)

    def rotate(self, to):
        self.userscanvas.delete('rr')
        self.userscanvas.delete('img')
        self.userscanvas.delete('menuline')

        alpha = (self.a % 360) * math.pi / 180
        points = round_rectangle_points(self.padding * self.scale[0], self.padding * self.scale[1],
                                        (self.w - self.padding) * self.scale[0],
                                        (self.h - self.padding) * self.scale[1], radius=64)
        rotate_polygon(points, (self.w / 2) * self.scale[0], self.h / 2, oy=alpha)
        self.userscanvas.create_polygon(points, fill='#91b0cf', tag='rr', smooth=True)

        # if self.a > 270 or self.a < 90:
        for i in range(3):
            points = round_rectangle_points((self.w * 0.85 - self.padding) * self.scale[0],
                                            (self.h / 10 + i * 8) * self.scale[1],
                                            (self.w * 0.95 - self.padding) * self.scale[0],
                                            (self.h / 10 + i * 8 + 3) * self.scale[1],
                                            )
            rotate_polygon(points, (self.w / 2) * self.scale[0], 0, oy=alpha)
            self.userscanvas.create_polygon(points, fill='#4978a6', tag='menuline', smooth=False)
        # else:
        #     for i in range(3):
        #         points = round_rectangle_points((self.w * 0.85 - self.padding) * self.scale[0],
        #                                         (self.h / 10 + i * 8) * self.scale[1],
        #                                         (self.w * 0.95 - self.padding) * self.scale[0],
        #                                         (self.h / 10 + i * 8 + 3) * self.scale[1],
        #                                         )
        #         rotate_polygon(points, (self.w / 2) * self.scale[0], 0, alpha)
        #         self.userscanvas.create_polygon(points, fill='#4978a6', tag='menuline')

        self.view(self.userscanvas, self.w, self.h, self.padding, self.scale, self.a)

        if self.a != to:
            self.a = (self.a + 5) % 360
            self.after(40, lambda: self.rotate(to))


class Wrap(tk.Frame):
    def __init__(self, parent, align):
        tk.Frame.__init__(self, parent)
        self.widgets = []
        self.align = align

    def add(self, *widgets):
        self.widgets += widgets
        for widget in widgets:
            widget.pack(side='left', anchor=self.align)

    def resize(self, w, h):
        for widget in self.widgets:
            widget.resize(w, h)


class Note(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.pages = []
        self.current_index = -1

    def add(self, *widgets):
        self.pages += widgets
        # for w in widgets:
        #      # w.grid(column = 0, row = 0)

    def select(self, page=None, previous=False, next=False):

        if self.current_index > -1:
            self.pages[self.current_index].forget()
        if isinstance(page, int):
            self.current_index = page
        elif previous:
            self.current_index = max(0, self.current_index - 1)
        elif next:
            self.current_index = min(self.pages.__len__() - 1, self.current_index + 1)
        else:
            for i in range(self.pages.__len__()):
                if self.pages[i] == page:
                    self.current_index = i
                    break
        # self.pages[page].tkraise()
        self.pages[self.current_index].pack(expand=tk.YES, fill=tk.BOTH, padx=0, pady=0, side='top')

    def resize(self, w, h, aw, ah, all=False):
        if all:
            for page in self.pages:
                if hasattr(page, 'resize'):
                    page.resize(w, h, aw, ah)
        elif hasattr(self.pages[self.current_index], 'resize'):
            self.pages[self.current_index].resize(w, h, aw, ah)


class TableWidget(tk.Frame):
    def __init__(self, parent, data, w=550, h=400, fields=['first_name', 'id', 'sex']):
        tk.Frame.__init__(self, parent)
        self.w = w
        self.h = h
        self.data = data
        self.scrollLists = {}
        self.fields = fields
        i = 0
        self.loadedIndexes = (0,0)
        self.loaded = True

        for field in self.fields:

            sl = ScrollList(self, choosable=True, loadcolor='#91b0cf', pointerup=self.pointerup,
                            pointerdown=self.pointerdown, moved=self.moved, padding=(10, 0, 10, 0), w=180, h=self.h,
                            fillcolor='white', borderradius=0, textcolor='#224b79', item_height=20, item_padding=5)
            hat = InputField(self, None, 0, 0, 180, 40, text = '', bg='#ffffff', empty_text=field,
                               on_enter=lambda a: print(a))
            hat.init_canvas()
            hat.grid(row=0, column=self.scrollLists.__len__(), sticky = 'n')
            hat = SimpleButton(self, text=field, w=180, h=40, borderradius=0,
                               onclicked=self.getLambda(self.sort, field))
            hat.grid(row=1, column=self.scrollLists.__len__(), sticky = 'n')
            self.scrollLists[field] = sl
        self.loadCanvas = canvas = tk.Canvas(self, width=self.w, height=self.h - 40)
        canvas.configure(bg='#f1f0ec')
        self.progressBar = ProgressBar(self, canvas, 550 / 2, 400 / 2, 40, 60, '#91b0cf', '#224b79')
        canvas.grid(column=0, row=2, columnspan=fields.__len__(), sticky='nsew')
        self.update()
        self.updateScrollLists(data)

    def getLambda(self, foo, arg):
        return lambda: foo(arg.encode().decode())

    def watch_load(self):
        if self.loaded:
            self.progressBar.working = False
            for scrollList in self.scrollLists.values():
                scrollList.updatecanvas()
            self.loadCanvas.grid_forget()
            i = 0
            for sl in self.scrollLists.values():
                sl.grid(row=2, column=i)
                i += 1
        else:
            print('Loading...')
            self.after(500, self.watch_load)

    def fill_scroll_lists(self, data, a = 0, b = 10):
        a = max(a, 0)
        b = min(b, self.data.__len__())

        if a < self.loadedIndexes[0]:
            a = a
        elif a < self.loadedIndexes[1]:
            a = self.loadedIndexes[1]
        else:
            a = a
        if b < a:
            self.loaded = True
            return
        if b < self.loadedIndexes[0]:
            b = b
        elif b < self.loadedIndexes[1]:
            b = self.loadedIndexes[0]
        else:
            b = b

        if a == b:
            self.loaded = True
            return

        # for i in range(a,  b, 1):
        #     if self.loadedIndexes[0] < i < self.loadedIndexes[1]:
        #         i = self.loadedIndexes[1]
        #     for field, scrollList in self.scrollLists.items():
        #         if field in data[i]:
        #             scrollList.add(data[i][field], update=False)
        #     i += 1
        #Для простоты пока пусть загружаются все строки от a (до b)
        for field, scrollList in self.scrollLists.items():
            users_list = data[a:b][field].tolist()
            for attribute in users_list:
                scrollList.add(attribute, update = False)
        self.loadedIndexes = (min(self.loadedIndexes[0], a), max(self.loadedIndexes[1], b) )
        self.loaded = True
        print('Filled ', self.loadedIndexes)

    def pointerdown(self, e):

        for scrollList in self.scrollLists.values():
            scrollList.pointerdown(e)

    def pointerup(self, e):
        for scrollList in self.scrollLists.values():
            scrollList.pointerup(e, update=False)
        for scrollList in self.scrollLists.values():
            scrollList.updatecanvas()

    def moved(self, e):

        for scrollList in self.scrollLists.values():
            scrollList.moved(e, update=False)

        for scrollList in self.scrollLists.values():
            scrollList.updatecanvas()
        visibleIndexes = self.scrollLists[self.fields[0]].getVisibleIndexes()
        if self.loadedIndexes[1] < visibleIndexes[1] + 5:
            self.fill_scroll_lists(self.data, visibleIndexes[1], visibleIndexes[1] + 50)
        if self.loadedIndexes[0] + 5 > visibleIndexes[0]:
            self.fill_scroll_lists(self.data, visibleIndexes[0] - 50, visibleIndexes[0])

    def sort(self, field, reverse=False):
        print(field)

        key = lambda item: item[field]
        thread = th.Thread(target=self.sort_data, args=([self.data, key, reverse]), daemon=True)
        thread.start()
        self.loadCanvas = canvas = tk.Canvas(self, width=self.w, height=self.h - 30)
        canvas.configure(bg='#f1f0ec')
        self.progressBar = ProgressBar(self, canvas, 550 / 2, 400 / 2, 40, 60, '#91b0cf', '#224b79')
        self.progressBar.drawprogress()
        canvas.grid(column=0, row=1, columnspan=self.scrollLists.__len__(), sticky='nsew')
        self.wait_for_sort()

    def selection(self):
        print('')

    def wait_for_sort(self):
        if self.loaded:
            print('Sorted')
            self.progressBar.working = False
            self.loadCanvas.grid_forget()
            for scrollList in self.scrollLists.values():
                scrollList.reset()
            self.updateScrollLists(self.data)
        else:
            self.after(500, self.wait_for_sort)

    def work(self, q):
        while True:
            foo, args = q.get()
            foo(args)
            q.task_done()

    def sort_data(self, data, key, reverse):
        self.loaded = False
        self.data = sorted(data, key=key, reverse=reverse)
        self.loaded = True

    def updateScrollLists(self, data):
        self.loaded = False
        th.Thread(target=self.fill_scroll_lists, args=([data]), daemon=True).start()
        self.progressBar.drawprogress()
        self.watch_load()


class RuMap(tk.Frame):
    def __init__(self, parent, coords=None, hower_callback=lambda n: (), w=360, h=155, scaleX=2):
        tk.Frame.__init__(self, parent)
        self.scaleX = scaleX
        self.coords = coords
        self.width = w
        self.height = h
        self.last_scale = 1
        self.hover_region_tag = ''
        self.hower_callback = hower_callback
        # F0F0ED
        c = tk.Canvas(self, width=w, height=h, bd=-2, bg='#F0F0ED')
        c.pack()
        c.bind("<Motion>", self.map_hover)
        self.canvas = c
        self.draw_map(c)

    def resize(self, w, h, aw, ah):
        current_scale = min(aw, ah) / self.last_scale
        self.canvas.configure(width=aw * self.width, height=min(aw, ah) * self.height)
        self.canvas.scale('all', 0, 0, current_scale, current_scale)
        self.last_scale = min(aw, ah)
        # self.draw_map(self.canvas, scale=self.scaleX * min(w,h))
        # resize(self.canvas, w, h)

    def map_hover(self, details, updateScrollList=True):
        reg = self.canvas.find_overlapping(details.x, details.y, details.x, details.y)
        if reg.__len__() > 0:
            name = self.canvas.itemcget(reg[0], 'tag').split('_')[0]
            if name != self.hover_region_tag:
                if self.hower_callback is not None:
                    self.hower_callback(name)
                self.canvas.tag_raise(name + '_shadow')
                self.canvas.move(name + '_shadow', 1, 1)
                self.canvas.tag_raise(name)
                self.canvas.move(name, -1, -1)
                self.canvas.tag_lower(self.hover_region_tag)
                self.canvas.move(self.hover_region_tag, 1, 1)
                self.canvas.tag_lower(self.hover_region_tag + '_shadow')
                self.canvas.move(self.hover_region_tag + '_shadow', -1, -1)
                self.hover_region_tag = name
        elif self.hover_region_tag != '':
            if self.hower_callback is not None:
                self.hower_callback('')
            self.canvas.tag_lower(self.hover_region_tag)
            self.canvas.move(self.hover_region_tag, 1, 1)
            self.canvas.tag_lower(self.hover_region_tag + '_shadow')
            self.canvas.move(self.hover_region_tag + '_shadow', -1, -1)
            self.hover_region_tag = ''

    def update_colors(self, regions, color_gradient):
        self.minreg = 999999
        self.maxreg = -99

        for reg in regions:
            self.minreg = min(self.minreg, regions[reg])
            self.maxreg = max(self.maxreg, regions[reg])

        # if regions.__len__() > 0:
        #     for reg in regions:
        #         self.scrollList.setProgress(name=reg.replace('RU-', ''), progress=self.regions[reg] / self.maxreg * 0.9,
        #                                     text=' ' + str(self.regions[reg]))
        #     self.scrollList.sort()
        for reg in self.coords:
            if reg['name'] in regions:
                try:
                    regcolor = color_gradient[
                        round((regions[reg['name']] - self.minreg) / (self.maxreg - self.minreg) * (
                                color_gradient.__len__() - 1))]
                except Exception as e:
                    regcolor = '#DDDDDD'
                    print(self.minreg, ' ', self.maxreg, ' ', regions[reg['name']], ' ', round(
                        (regions[reg['name']] - self.minreg) / (self.maxreg - self.minreg) * (
                                color_gradient.__len__() - 1)))

            else:
                regcolor = '#DDDDDD'
            self.canvas.itemconfigure(reg['name'], fill=regcolor)

    def draw_map(self, c, scale=-1):
        scale = scale if scale > 0 else self.scaleX
        c.delete('all')
        for reg in self.coords:
            for poly in reg['coordinates'][0]:
                poly_coords = []
                scaleY = scale * 5 / 3
                offX = -15
                offY = 85
                for point in poly:
                    poly_coords += [(offX + point[1]) * scale, (offY - point[0]) * scaleY]
                c.create_polygon(poly_coords, fill='black', outline='black', tag=reg['name'] + '_shadow')
                c.create_polygon(poly_coords, fill='#DDDDDD', outline='black', tag=reg['name'])


def resize(canvas, wscale, hscale):
    print('resize ', wscale, '  ', hscale)
    # wscale = float(event.width)/self.width
    # hscale = float(event.height)/self.height
    scale = min(wscale, hscale)
    # self.width = self.width* scale
    # self.height = self.height * scale
    # canvas.config(width=self.width, height=self.height)
    canvas.scale("all", 0, 0, scale, scale)


def getPolygons(s, scale=1.0, offsetX=0, offsetY=0):
    polygons = []
    points = []
    pointsBezue = []
    buildCurve = False
    start = (0, 0)
    s = list(filter(lambda a: a is not None and a != ' ' and a != '',
                    re.split('([a-zA-Z])|(\-\d+\.\d+)|(\-\d+)|(\.\d+)|(\d+\.\d+)|(\d+)', s.replace(',', ' '))))

    i = 0
    while i < s.__len__():
        if s[i][0] == 'h':
            buildCurve = False
            i += 1
            points.append(float(s[i]) * scale + points[-2])
            points.append(points[-2])
            i += 1
        elif s[i][0] == 'v':
            buildCurve = False
            i += 1
            points.append(points[-2])
            points.append(float(s[i]) * scale + points[-2])
            i += 1

        elif s[i][0] == 'l':
            buildCurve = False
            i += 1
            points.append(float(s[i]) * scale + points[-2])
            i += 1
            points.append(float(s[i]) * scale + points[-2])
            i += 1

        elif s[i][0] == 't':
            i += 1
            pointsBezue.append(float(s[i]) * scale + pointsBezue[-2])
            i += 1
            pointsBezue.append(float(s[i]) * scale + pointsBezue[-2])
            points += getBezue(pointsBezue)
            del pointsBezue[0]
            del pointsBezue[0]
            i += 1
        elif s[i][0] == 'q':
            i += 1
            pointsBezue.append(float(s[i]) * scale + points[-2])
            i += 1
            pointsBezue.append(float(s[i]) * scale + points[-2])
            i += 1
            pointsBezue.append(float(s[i]) * scale + pointsBezue[-2])
            i += 1
            pointsBezue.append(float(s[i]) * scale + pointsBezue[-2])
            pointsBezue.insert(0, points[-2])
            pointsBezue.insert(1, points[-1])
            del points[-1]
            del points[-1]
            points += getBezue(pointsBezue)
            i += 1
        elif s[i][0] == 'z' or s[i][0] == 'Z':
            i += 1
        elif s[i][0] == 'M':
            buildCurve = False
            if points.__len__() > 0:
                polygons.append(points)
                points = []
            if s[i] == 'M':
                i += 1
            else:
                s[i] = s[1:]
        elif s[i] == 'C':
            buildCurve = True
            i += 1
        elif s[i] == 'L':
            buildCurve = False
            i += 1
            points.append(float(s[i]) * scale + offsetX - start[0])
            i += 1
            points.append(float(s[i]) * scale + offsetY - start[1])
            i += 1
        else:
            x = float(s[i]) * scale + offsetX - start[0]
            i += 1
            y = float(s[i]) * scale + offsetY - start[1]
            i += 1
            if start[0] == 0 and start[1] == 0:
                start = (x - offsetX, y - offsetY)
                points = [offsetX, offsetY]
                continue
            if buildCurve:
                pointsBezue.append(x)
                pointsBezue.append(y)
                if pointsBezue.__len__() == 6:
                    points += getBezue([points[-2], points[-1]] + pointsBezue)
                    pointsBezue = []
            else:
                points.append(x)
                points.append(y)

    polygons.append(points)
    return polygons


def getBezue(points_in):
    points = []
    if points_in.__len__() == 8:
        for i in range(0, 10, 1):
            t = i / 10
            x = (points_in[0] * (1 - t) ** 3 + points_in[2] * 3 * t * (1 - t) ** 2 + points_in[4] * 3 * t ** 2 * (
                    1 - t) +
                 points_in[6] * t ** 3)
            y = (points_in[1] * (1 - t) ** 3 + points_in[3] * 3 * t * (1 - t) ** 2 + points_in[5] * 3 * t ** 2 * (
                    1 - t) +
                 points_in[7] * t ** 3)
            points.append(x)
            points.append(y)
    elif points_in.__len__() == 6:
        for i in range(0, 10, 1):
            t = i / 10
            x = points_in[0] * (1 - t) ** 2 + points_in[2] * 2 * t * (1 - t) + points_in[4] * t ** 2
            y = points_in[1] * (1 - t) ** 2 + points_in[3] * 2 * t * (1 - t) + points_in[5] * t ** 2
            points.append(x)
            points.append(y)
    return points


def fit_text(w, h, text, font):
    canvas = tk.Canvas()
    ctext = canvas.create_text(100, 100, text=text, font=font)
    box = canvas.bbox(ctext)
    while (box[2] - box[0] > w or (box[3] - box[1]) > h):
        font = (font[0], font[1] - 1)
        ctext = canvas.create_text(100, 100, text=text,
                                   font=font)
        box = canvas.bbox(ctext)
    while box[2] - box[0] < w and box[3] - box[1] < h:
        font = (font[0], font[1] + 1)
        ctext = canvas.create_text(100, 100, text=text,
                                   font=font)
        box = canvas.bbox(ctext)
    return font


def rotate_polygon(points, x, y, ox=0, oy=0, oz=0):
    if oy != 0:
        for i in range(0, points.__len__(), 2):
            points[i] = x + (points[i] - x) * math.cos(oy)
    if ox != 0:
        for i in range(0, points.__len__(), 2):
            points[i + 1] = y + (points[i + 1] - y) * math.cos(ox)
    if oz != 0:
        for i in range(0, points.__len__(), 2):
            tx = x + (points[i] - x) * math.cos(oz) - (points[i + 1] - y) * math.sin(oz)
            ty = y + (points[i] - x) * math.sin(oz) + ((points[i + 1] - y) * math.cos(oz))
            points[i], points[i + 1] = tx, ty
