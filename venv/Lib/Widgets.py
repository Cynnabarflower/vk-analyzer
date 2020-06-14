import tkinter as tk
from tkinter import ttk
import math
import threading as th
from multiprocessing import Queue
import re
import time
import pandas as pd
import json

BUTTON_WIDTH = 245
BUTTON_HEIGHT = 50
PADDING = 10
CITIES = None


class NavBar(tk.Frame):
    def __init__(self, parent, w=550, h=50, backgroundcolor='#4978a6', onclicked=(), pages=None, textcolor='#cadef7',
                 choosedcolor="#44ff44", borderradius=18, fillcolor='#224b79', padding=10, button_width=100):
        tk.Frame.__init__(self, parent)
        if pages is None:
            pages = []
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
        """
        Show changes on canvas
        """
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
        """
        If page button is clicked - changes the page
        :param e:
        :type e:
        """
        if (e.y > self.padding and e.y < self.w - self.padding):
            for i in range(self.buttons.__len__()):
                if (e.x >= self.buttons[i][0] and e.x <= self.buttons[i][1]):
                    self.currentPage = i
                    self.onclicked(i)
                    self.updatecanvas()
                    break


class HorizontalScrollBar(tk.Frame):
    def __init__(self, parent, w=200, h=20, car_w=20, car_h=20, car_color='#4978a6', fill_color='#91b0cf', bg='#f1f0ec',
                 callback=None):
        tk.Frame.__init__(self, parent)
        self.progress = 0
        self.h = h
        self.w = w
        self.min = self.max = 0
        self.set_min_max(min=0, max=1)
        self.scale = (1, 1)
        self.last_progress = self.min
        self.car_w = car_w
        self.car_h = car_h
        self.car_color = car_color
        self.fill_color = fill_color
        self.bg = bg
        self.callback = callback
        self.canvas = tk.Canvas(self, width=w, height=h, bd=-2, bg=bg)
        self.initcanvas()
        self.canvas.bind("<B1-Motion>", self.moved)
        self.canvas.bind("<Button-1>", self.pointer_down)
        self.canvas.pack()

    def pointer_down(self, d):
        self.pointer_x = d.x
        print('down', d.x)
        self.set_progress((self.pointer_x - self.car_w / 2) / (self.w * self.scale[0] - self.car_w))
        if self.callback:
            self.callback(self.progress)
            self.updatecanvas()
            self.pointer_x = self.car_w / 2

    def moved(self, d):
        """
        Moves the cart
        :param d:
        :type d:
        """
        self.set_progress((d.x - self.pointer_x) / (self.w * self.scale[0] - self.car_w))
        print(self.progress)
        if self.callback:
            self.callback(self.progress)
        self.updatecanvas()

    def set_progress(self, progress):
        self.last_progress = self.progress
        self.progress = progress
        self.progress = min(self.max, max(self.progress, self.min))

    def resize(self, w, h, aw, ah):
        self.canvas.configure(width=self.w * aw)
        self.scale = (aw, ah)
        self.initcanvas()
        self.last_progress = 0
        self.updatecanvas()

    def set_min_max(self, min=None, max=None):
        if min is not None:
            self.min = min
        if max is not None:
            self.max = max

    def initcanvas(self):
        """
        Initializes canvas
        """
        self.canvas.delete('ALL')
        self.canvas.create_polygon(
            round_rectangle_points(
                0, 0, self.w * self.scale[0], self.h, radius=self.h / 4
            ), fill=self.fill_color, smooth=True
        )
        x = 0 * self.scale[0] / abs(self.max - self.min) * self.w
        self.pointer = self.canvas.create_polygon(
            round_rectangle_points(x, (self.h - self.car_h) / 2, x + self.car_w, self.car_h, radius=self.car_h / 4)
            , fill=self.car_color, smooth=True
        )

    def updatecanvas(self):
        """
        Updates canvas
        """
        self.canvas.move(self.pointer, (self.w * self.scale[0] - self.car_w) * (self.progress - self.last_progress), 0)


class ScrollList(tk.Frame):
    def __init__(self, parent, w=BUTTON_WIDTH + 2 * PADDING, h=(BUTTON_HEIGHT + PADDING) * 4 + PADDING / 2,
                 bg='#f1f0ec', onclicked=(), ondblclicked=(), items=[], textcolor='#ffffff', figurecolor=None,
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
        self.ondblclicked = ondblclicked
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
        c.bind('<Double-Button-1>', self.dblclicked)
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
        self.visibleheight = min(
            self.h - max(self.buttons.__len__(), 5) * (self.item_height + self.item_padding) - self.padding[0] -
            self.padding[
                2],
            0)
        c.pack()
        self.initcanvas()
        self.updatecanvas()

    def add(self, element, update=True):
        """
        Adds new element on scrollList
        :param element:
        :type element:
        :param update:
        :type update:
        """
        if not isinstance(element, ScrollListButton):
            self.buttons.append(
                ScrollListButton('item' + str(self.nextTag), y=0, value=element, fillcolor=self.fillcolor,
                                 choosable=self.choosable, borderradius=self.borderraadius,
                                 loadcolor=self.loadcolor, textcolor=self.textcolor)
            )
            font = fit_text(self.item_width * 0.9 - 2, self.item_height * 0.9 - 2, element,
                            (self.buttons[-1].font, self.buttons[-1].fontsize))
            self.buttons[-1].font = font[0]
            self.buttons[-1].fontsize = font[1]
        else:
            element.tag = 'item' + str(self.nextTag)
            self.buttons.append(element)
        self.nextTag += 1

        self.visibleheight = min(
            self.h - self.buttons.__len__() * (self.item_height + self.item_padding) - self.padding[0] - self.padding[
                2],
            0)

        if update:
            self.updatecanvas()

    def remove(self, i=-1, button=None, name='', stage=1):
        """
        removes element from scrolllist
        :param i:
        :type i:
        :param button:
        :type button:
        :param name:
        :type name:
        :param stage:
        :type stage:
        """
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
        """
        Removes all elements and updates canvas
        """
        self.nextTag = 0
        self.dy = 0
        self.canvas.delete('all')
        self.buttons.clear()
        self.updatecanvas()

    def resize(self, w, h, aw, ah, only_canvas=False):
        self.canvas.configure(width=self.w * aw, height=self.h * ah)
        self.scale = (aw, ah)
        if only_canvas:
            self.updateframe()
            return
        self.canvas.delete('all')
        self.initcanvas()

    def initcanvas(self):
        """
        Inits canvas
        """
        if self.figurecolor is not None:
            round_rectangle(self.canvas, self.padding[3], self.padding[0], self.w * self.scale[0] - self.padding[1],
                            (self.h * self.scale[1]) - self.padding[2], radius=32, fill=self.figurecolor)
        y = self.dy + self.item_padding + self.padding[0]
        for button in self.buttons:
            self.draw_new(button, y)
            y += (self.item_height + self.item_padding)
        self.updateframe()

    def updateframe(self):
        """
        Updates frame on canvas
        Frame covers elements
        """
        self.canvas.delete('frame')
        self.canvas.create_rectangle(self.padding[3], 0, self.w * self.scale[0] - self.padding[1], self.padding[0],
                                     outline=self.backgroundcolor,
                                     fill=self.backgroundcolor, tag='frame')
        self.canvas.create_rectangle(self.padding[3], self.h * self.scale[1] - self.padding[2],
                                     self.w * self.scale[0] - self.padding[1],
                                     self.h * self.scale[1], outline=self.backgroundcolor,
                                     fill=self.backgroundcolor, tag='frame')

    def update_button(self, button, y):
        """
        Updates elements:
        Shows progress, updates text, changes position, deletes
        :param button:
        :type button:
        :param y:
        :type y:
        """
        if not button.needsupdate:
            if y != button.y:
                self.canvas.move(button.tag, 0, y - button.y)
                self.canvas.move(button.tag + 'progress', 0, y - button.y)
                self.canvas.move(button.tag + 'text', 0, y - button.y)
                button.set_y(y)

        else:
            self.canvas.delete(button.tag)
            self.canvas.delete(button.tag + 'text')
            self.canvas.delete(button.tag + 'progress')
            self.draw_new(button, y)

    def getVisibleIndexes(self):
        """
        Returns min and max indexes for visible elements
        :return:
        :rtype:
        """
        block_height = (self.item_height + self.item_padding)
        y = self.dy + self.item_padding + self.padding[0]
        b = max(math.floor(-y / block_height), 0)
        e = min(b + math.floor(self.h * self.scale[1] / block_height) + 2, self.buttons.__len__())
        return (b, e)

    def updatecanvas(self):
        """
        Updates elemets on canvas
        :return:
        :rtype:
        """
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
                for button, k in self.moved_buttons.items():
                    self.update_button(button, self.dy + self.item_padding + self.padding[0] + k * (
                            self.item_height + self.item_padding))
                break
            if button in self.moved_buttons:
                del self.moved_buttons[button]
            self.update_button(button, y)
            y += (self.item_height + self.item_padding)
        self.canvas.tag_raise('frame')
        self.update()

    def draw_new(self, button, y):
        """
        Draws new element
        Called when the element is new or needs lot of changes
        :param button:
        :type button:
        :param y:
        :type y:
        """
        x0 = self.padding[3] + (
                self.w * self.scale[0] - self.padding[1] - self.padding[3] - self.item_width * self.scale[0]) / 2
        x1 = x0 + self.item_width * self.scale[0]

        button.draw_back(self.canvas, x0, y, x1, y + self.item_height)

        button.draw_chosen(self.canvas, x0, y, x1, y + self.item_height)

        button.draw_progress(self.canvas, x0 + self.progress_offset * self.scale[0],
                             y,
                             x1 - self.progress_offset * self.scale[0],
                             y + self.item_height)

        button.draw_text(self.canvas, x0, y, x1, y + self.item_height)

        button.set_y(y)
        button.needsupdate = False

    def sort(self, key=lambda item: item.progress, reverse=True, update=True):
        """
        Sorts elements by key
        if update s true - updates canvas
        :param key:
        :type key:
        :param reverse:
        :type reverse:
        :param update:
        :type update:
        """
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
        """
        Changes element position among others
        :param name:
        :type name:
        :param pos:
        :type pos:
        :param up:
        :type up:
        :param down:
        :type down:
        :return:
        :rtype:
        """
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
        """
        Handles element choose
        :param e:
        :type e:
        :param i:
        :type i:
        """
        if self.buttons[i].choosable:
            self.buttons[i].chosen()
            self.updatecanvas()
        if self.onclicked:
            self.onclicked(self.buttons[i])

    def dblclicked(self, e):
        """
        Handles double click
        :param e:
        :type e:
        :return:
        :rtype:
        """
        if e.y > self.padding[0] and e.y < self.h * self.scale[1] - self.padding[2]:
            if self.ondblclicked:
                for i in range(self.buttons.__len__()):
                    if e.y >= self.buttons[i].y and e.y <= self.buttons[i].y + self.item_height:
                        self.ondblclicked(self.buttons[i])
                        return

    def pointerup(self, e, update=True):
        """
        Handles clicks
        :param e:
        :type e:
        :param update:
        :type update:
        :return:
        :rtype:
        """
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

    def pointerdown(self, e):
        print('Scrollbox down')
        self.pointerx = e.x
        self.pointery = e.y
        self.lasty = e.y

    def moved(self, d, update=True):
        """
        Handles drag
        :param d:
        :type d:
        :param update:
        :type update:
        """
        ndy = d.y - self.lasty if d.delta == 0 else self.item_height * d.delta / 100
        self.dy = self.dy + ndy
        self.dy = min(self.padding[2] + self.item_padding, self.dy + ndy) if ndy > 0 else max(self.dy + ndy,
                                                                                              self.visibleheight -
                                                                                              self.padding[0])
        if update:
            self.updatecanvas()
        self.lasty = d.y

    def setProgress(self, i=-1, name='', progress=0, text=''):
        """
        Sets element's progress (0 - 1.0)
        :param i:
        :type i:
        :param name:
        :type name:
        :param progress:
        :type progress:
        :param text:
        :type text:
        """
        if i > -1:
            self.buttons[i].set_progress(progress)
            if text is not None:
                self.buttons[i].set_text(self.buttons[i].value + text)

        else:
            for button in self.buttons:
                if button.value == name:
                    button.set_progress(progress)
                    if text is not None:
                        button.set_text(button.value + text)
                    break
        self.updatecanvas()


class ScrollListButton:
    def __init__(self, tag, y, value=None, text=None, font='Colibri', fontsize=25, progress=0, fillcolor='#ffffff',
                 choosable=False, borderradius=6, loadcolor='red', textcolor='white'):
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
        self.borderradius = borderradius
        self.loadcolor = loadcolor
        self.textcolor = textcolor

    def draw_back(self, canvas, x0, y0, x1, y1):
        """
        Draws background figure of the element
        :param canvas:
        :type canvas:
        :param x0:
        :type x0:
        :param y0:
        :type y0:
        :param x1:
        :type x1:
        :param y1:
        :type y1:
        """
        if self.fillcolor is not None:
            round_rectangle(canvas, x0, y0, x1, y1,
                            radius=self.borderradius, outline=self.fillcolor,
                            fill=self.fillcolor, tag=self.tag)

    def draw_chosen(self, canvas, x0, y0, x1, y1):
        """
        Draws background figure of choosen elements
        :param canvas:
        :type canvas:
        :param x0:
        :type x0:
        :param y0:
        :type y0:
        :param x1:
        :type x1:
        :param y1:
        :type y1:
        """
        if self.isChosen:
            round_rectangle(canvas, x0, y0, x1, y1,
                            radius=self.borderradius, outline=self.loadcolor,
                            fill=self.loadcolor, tag=self.tag)

    def draw_progress(self, canvas, x0, y0, x1, y1):
        """
        Draws progress
        :param canvas:
        :type canvas:
        :param x0:
        :type x0:
        :param y0:
        :type y0:
        :param x1:
        :type x1:
        :param y1:
        :type y1:
        """
        if self.progress > 0.02:
            round_rectangle(canvas, x0, y0,
                            ((x1 - x0) * self.progress + x0),
                            y1,
                            radius=self.borderradius, outline=self.loadcolor, fill=self.loadcolor,
                            tag=self.tag + 'progress')
        elif self.progress > 0:
            canvas.create_rectangle(x0, y0, ((x1 - x0) * self.progress + x0),
                                    y1, outline=self.loadcolor, fill=self.loadcolor,
                                    tag=self.tag + 'progress')

    def draw_text(self, canvas, x0, y0, x1, y1):
        """
        Draws text
        :param canvas:
        :type canvas:
        :param x0:
        :type x0:
        :param y0:
        :type y0:
        :param x1:
        :type x1:
        :param y1:
        :type y1:
        """
        canvas.create_text((x1 + x0) / 2, (y0 + y1) / 2, text=str(self.text),
                           fill=self.textcolor,
                           font=fit_text((x1 - x0) * 0.8, (y1 - y0) * 0.9, self.text, (self.font, self.fontsize)),
                           tag=self.tag + 'text')

    def chosen(self, chosen=None):
        """
        Setter for chosen
        :param chosen:
        :type chosen:
        """
        if (chosen == None or chosen != self.isChosen):
            self.isChosen = not self.isChosen
            self.needsupdate = True

    def set_text(self, text):
        """
        Text setter
        :param text:
        :type text:
        """
        self.text = text
        self.needsupdate = True

    def set_progress(self, progress):
        """
        Progress setter
        :param progress:
        :type progress:
        """
        self.progress = progress
        self.needsupdate = True

    def set_y(self, y):
        """
        Position setter
        :param y:
        :type y:
        """
        self.old_y = self.y
        self.y = y

class WideScrollListButton(ScrollListButton):
    def __init__(self, tag, y, values=None, text=None, font='Colibri', fontsize=25, progress=0, fillcolor='#ffffff',
                 choosable=False, borderradius=6, loadcolor='red', textcolor='white', parts=6, step=None):

        ScrollListButton.__init__(self, tag, y, value='', text='', font=font, fontsize=fontsize, progress=progress,
                                  fillcolor=fillcolor, choosable=choosable,
                                  borderradius=borderradius, loadcolor=loadcolor, textcolor=textcolor)
        self.value = values
        self.text = text if text is not None else list(map(lambda a: str(a), values))
        self.parts = parts
        self.step = step

    def draw_back(self, canvas, x0, y0, x1, y1):
        if self.fillcolor is not None:
            round_rectangle(canvas, x0, y0, x0 + (x1 - x0) * max(1, self.text.__len__() / self.parts), y1,
                            radius=self.borderradius, outline=self.fillcolor,
                            fill=self.fillcolor, tag=self.tag)

    def draw_chosen(self, canvas, x0, y0, x1, y1):
        if self.isChosen:
            round_rectangle(canvas, x0, y0, x0 + (x1 - x0) * max(1, self.text.__len__() / self.parts), y1,
                            radius=self.borderradius, outline=self.loadcolor,
                            fill=self.loadcolor, tag=self.tag)

    def draw_text(self, canvas, x0, y0, x1, y1):
        step = self.step if self.step else ((x1 - x0) / self.parts)
        for text_item in self.text:
            canvas.create_text(x0 + step / 2, (y0 + y1) / 2, text=str(text_item),
                               fill=self.textcolor,
                               font=fit_text(step * 0.9, (y1 - y0), str(text_item), (self.font, self.fontsize)),
                               tag=self.tag + 'text')
            x0 += step


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
        """
        Adjustes text size to fit button size
        """
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
        """
        Resizes button
        :param w:
        :type w:
        :param h:
        :type h:
        :param aw:
        :type aw:
        :param ah:
        :type ah:
        """
        self.scale = (aw, ah)
        self.canvas.configure(height=self.h * ah, width=self.w * aw)
        self.fit_text()
        self.canvas.delete('all')
        self.updatecanvas()

    def clicked(self, e):
        """
        Click handle
        :param e:
        :type e:
        """
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
        """
        Updates element on canvas
        """
        self.canvas.delete('text')
        self.canvas.delete('progress')
        round_rectangle(self.canvas, self.padding * self.scale[0], self.padding * self.scale[1],
                        (self.w - self.padding) * self.scale[0], (self.h - self.padding) * self.scale[1],
                        radius=self.borderradius * self.scale[0], outline=self.fillcolor, fill=self.fillcolor)
        # self.canvas.create_rectangle(0, 0, prorgess / 100 * self.w, self.h, outline=self.backgroundcolor, fill=self.backgroundcolor)
        self.canvas.create_text(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2, text=self.text,
                                fill=self.textcolor, font=self.font, tag='text')

    def drawProgress(self, prorgess):
        """
        Updates progress
        :param prorgess:
        :type prorgess:
        """
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
        self.visible = True
        self.working = False
        self.scale = (1, 1)
        self.fit_text()
        for point in self.points1:
            canvas.create_polygon(point, fill=color1, smooth=True, tag='outer_' + self.id)
        self.canvas.create_polygon(ProgressBar.getcircle(x, y, r1, r2, 0), fill=self.color2, smooth=False,
                                   tag='inner_' + self.id)
        self.canvas.create_text(x, y, text='0', font=self.font, fill=color2, tag='progress_' + self.id)

    def set_visible(self, visible):
        self.visible = visible

    def fit_text(self):
        """
        Adjustes font size to fit button size
        """
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
        """
        Draws progress on canvas
        finite or infinite
        :param progress:
        :type progress:
        :return:
        :rtype:
        """
        if not self.working:
            self.canvas.delete('inner_' + self.id)
            self.canvas.itemconfigure('outer_' + self.id, state='hidden')
            self.canvas.itemconfigure('progress_' + self.id, state='hidden')
            return
        if not self.visible:
            self.canvas.itemconfigure('outer_' + self.id, state='hidden')
            self.canvas.itemconfigure('progress_' + self.id, state='hidden')
            self.canvas.itemconfigure('inner' + self.id, state='hidden')
        else:
            self.canvas.itemconfigure('outer_' + self.id, state='normal')
            self.canvas.itemconfigure('progress_' + self.id, state='normal')
            self.canvas.itemconfigure('inner' + self.id, state='normal')

        self.canvas.lift('outer_' + self.id)
        if progress >= 0:
            if self.visible:
                self.canvas.delete('inner_' + self.id)
                self.canvas.create_polygon(ProgressBar.getcircle(self.x, self.y, r1, r2, progress_to=progress),
                                           fill=self.color2, smooth=True, tag='inner_' + self.id)
                self.canvas.itemconfigure('progress_' + self.id, text=str(math.floor(progress * 100)))
        else:
            to = (self.progress + 0.1) / 5
            if self.visible:
                self.canvas.delete('inner_' + self.id)
                for point in ProgressBar.getcircle(self.x, self.y, self.r1, self.r2, progress_from=self.progress / 5,
                                                   progress_to=to, width=0.1, step=0.1):
                    self.canvas.create_polygon(point, fill=self.color2, smooth=False,
                                               tag='inner_' + self.id)
                self.canvas.itemconfigure('progress_' + self.id, text=str(math.floor(self.time)))
            self.progress = (self.progress + 0.1) % 10
            self.time += 0.1
            self.controller.after(100, self.drawprogress)

    def move(self, x, y):
        """
        Moves progress bar on canvas
        :param x:
        :type x:
        :param y:
        :type y:
        """
        self.canvas.move('progress_' + self.id, x - self.x, y - self.y)
        self.canvas.delete('outer_' + self.id)
        self.x = x
        self.y = y
        self.points1 = ProgressBar.getcircle(x, y, self.r1, self.r2, progress_from=0, progress_to=1, width=6.283 / 360,
                                             step=6.283 / 360)
        for point in self.points1:
            self.canvas.create_polygon(point, fill=self.color1, smooth=True, tag='outer_' + self.id)

    @staticmethod
    def getcircle(x, y, r1, r2, progress_from=0, progress_to=1, width=0.0875, step=0.0875):
        """
        Returns circle shaped points
        :param x:
        :type x:
        :param y:
        :type y:
        :param r1:
        :type r1:
        :param r2:
        :type r2:
        :param progress_from:
        :type progress_from:
        :param progress_to:
        :type progress_to:
        :param width:
        :type width:
        :param step:
        :type step:
        :return:
        :rtype:
        """
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
                x2, y2,
                x3, y3,
                x4, y4,
            ])
            t += step

        return points


class SimpleButton(tk.Frame):

    def __init__(self, parent, w=BUTTON_WIDTH + 2 * PADDING, h=BUTTON_HEIGHT + 2 * PADDING, backgroundcolor='#f1f0ec',
                 onclicked=None, text='', icon=None, textcolor='#ffffff',
                 fillcolor="#4978a6", loadcolor='#224b79', borderradius=18, padding=10, font=("Colibri", 25),
                 fixed=False):
        tk.Frame.__init__(self, parent, highlightthickness=0)
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
        self.clickable_polygon = -1
        c = tk.Canvas(self, width=w, height=h, bg=self.backgroundcolor, bd=-2)
        c.bind("<Button-1>", self.clicked)
        c.pack()
        self.canvas = c
        self.fit_text()
        self.updatecanvas(self.fillcolor)

    def set_text(self, text):
        """
        Sets button's text
        :param text:
        :type text:
        """
        self.text = text
        self.font = fit_text((self.w - self.padding * 2) * self.scale[0] * 0.8,
                             (self.h - self.padding * 2) * self.scale[1] * 0.8, self.text, self.font)

    def fit_text(self):
        """
        Adjustes text size to fit buttons size
        """
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

    def rotate(self, ox=0, oy=0, oz=0):
        """
        Rotates figure
        :param ox:
        :type ox:
        :param oy:
        :type oy:
        :param oz:
        :type oz:
        """
        self.rotation = [ox, oy, oz]
        self.updatecanvas(self.fillcolor)

    def resize(self, w, h, aw, ah):
        """
        Resizes button
        :param w:
        :type w:
        :param h:
        :type h:
        :param aw:
        :type aw:
        :param ah:
        :type ah:
        """
        self.scale = (aw, ah)
        self.canvas.configure(height=self.h * ah, width=self.w * aw)
        self.fit_text()
        self.updatecanvas(self.fillcolor)

    def clicked(self, e):
        """
        Click handler
        :param e:
        :type e:
        """
        if self.clickable_polygon in self.canvas.find_overlapping(e.x, e.y, e.x, e.y):
            if self.fixed:
                self.state = not self.state
                self.updatecanvas(self.loadcolor if self.state else self.fillcolor)
                if self.onclicked is not None:
                    if self.onclicked.__code__.co_argcount > 1 or self.onclicked.__code__.co_argcount == 1 and not 'self' in self.onclicked.__code__.co_varnames:
                        self.onclicked(self)
                    else:
                        self.onclicked()
                # self.updatecanvas(self.loadcolor if not self.state else self.fillcolor)
            else:
                self.updatecanvas(self.loadcolor)
                if self.onclicked is not None:
                    if self.onclicked.__code__.co_argcount > 1 or self.onclicked.__code__.co_argcount == 1 and not 'self' in self.onclicked.__code__.co_varnames:
                        self.onclicked(self)
                    else:
                        self.onclicked()
                self.updatecanvas(self.fillcolor)

    def updatecanvas(self, color=None):
        """
        Shows changes on canvas
        :param color:
        :type color:
        """
        self.canvas.delete('all')
        color = self.fillcolor if color is None else color
        rrp = round_rectangle_points(self.padding * self.scale[0], self.padding * self.scale[1],
                                     (self.w - self.padding) * self.scale[0], (self.h - self.padding) * self.scale[1],
                                     radius=self.borderradius)
        rotate_polygon(rrp, self.w * self.scale[0] / 2, self.h / 2 * self.scale[1], ox=self.rotation[0],
                       oy=self.rotation[1], oz=self.rotation[2])
        self.clickable_polygon = self.canvas.create_polygon(rrp, outline=color, fill=color, smooth=True)
        # round_rectangle(self.canvas, self.padding * self.scale[0], self.padding * self.scale[1],
        #                 (self.w - self.padding) * self.scale[0], (self.h - self.padding) * self.scale[1],
        #                 radius=self.borderradius, outline=color, fill=color)
        if self.icon is not None:
            if self.text == '':
                self.canvas.create_image(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2, image=self.icon,
                                         anchor='center')
            else:
                self.canvas.create_image(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2, image=self.icon,
                                         anchor='center')
        self.canvas.create_text(self.w * self.scale[0] / 2, self.h * self.scale[1] / 2, text=self.text,
                                fill=self.textcolor, font=self.font)


class RadioButton(tk.Frame):
    def __init__(self, parent, header_template=None, child_template=None, can_choose_multiple=False, onclicked=None):
        tk.Frame.__init__(self, parent)
        self.scale = (1, 1)
        self.header = None
        self.values = []
        self.can_choose_multiple = can_choose_multiple
        self.chosenButtons = []
        self.chosen_values = []
        self.onclicked = onclicked

        if header_template or child_template:
            if header_template and not child_template:
                child_template = header_template
            elif child_template and not header_template:
                header_template = child_template
        else:
            raise Exception('Must have at least one template')
        self.header_template = header_template
        self.child_template = child_template
        self.header_template.canvas.forget()
        self.child_template.canvas.forget()

    def set_header(self, value):
        """
        Sets header text
        :param value:
        :type value:
        """
        if self.header:
            self.header.grid_forget()
        self.header = SimpleButton(
            self,
            w=self.header_template.w,
            h=self.header_template.h,
            backgroundcolor=self.header_template.backgroundcolor,
            onclicked=None, text=value, icon=None, textcolor=self.header_template.textcolor,
            fillcolor=self.header_template.fillcolor, loadcolor=self.header_template.loadcolor,
            borderradius=self.header_template.borderradius,
            padding=self.header_template.padding, font=self.header_template.font
        )
        self.header.value = value
        self.header.grid(column=0, row=0)
        self.header.updatecanvas()

    def add_value(self, value):
        """
        Add new button with value
        :param value:
        :type value:
        """
        child = SimpleButton(
            self,
            w=self.child_template.w,
            h=self.child_template.h,
            backgroundcolor=self.child_template.backgroundcolor,
            onclicked=None, text=value, icon=None, textcolor=self.child_template.textcolor,
            fillcolor=self.child_template.fillcolor, loadcolor=self.child_template.loadcolor,
            borderradius=self.child_template.borderradius,
            padding=self.child_template.padding, font=self.child_template.font, fixed=True
        )
        child.onclicked = lambda a: self.chosen(a)
        child.grid(column=1 + self.children.__len__(), row=0)
        child.updatecanvas()
        self.values.append(child)

    def reset(self):
        """
        Unchoses all buttons
        """
        for button in self.chosenButtons:
            button.state = False
            button.updatecanvas()
        self.chosenButtons.clear()

    def chosen(self, button):
        """
        Handle button choose
        :param button:
        :type button:
        """
        print('chosen ', button.text)
        if not self.can_choose_multiple:
            for button1 in self.chosenButtons:
                if button1 == button:
                    continue
                print('unchosen ', button1.text)
                button1.state = False
                button1.updatecanvas()
            self.chosenButtons = [button]
        else:
            if button.state:
                self.chosenButtons.append(button)
            else:
                self.chosenButtons.remove(button)
        if self.onclicked:
            self.onclicked(self.get_selected())

    def get_selected(self):
        """
        Reterns selected values
        :return:
        :rtype:
        """
        values = []
        for button in self.chosenButtons:
            values.append(button.text)
        return values

    def remove_value(self, value):
        """
        Removes button with value
        :param value:
        :type value:
        """
        for child in self.values:
            if child.value == value:
                self.values.remove(child)

    def resize(self, w, h, aw, ah):
        """
        Resize buttons
        :param w:
        :type w:
        :param h:
        :type h:
        :param aw:
        :type aw:
        :param ah:
        :type ah:
        """
        if self.header:
            self.header.resize(w, h, aw, ah)
        for child in self.values:
            child.resize(w, h, aw, ah)



def round_rectangle(canvas, x1, y1, x2, y2, radius=25, radius1=None, radius2=None, radius3=None, radius4=None,
                    **kwargs):
    """
    Draws rounded rectangle on canvas
    :param canvas:
    :type canvas:
    :param x1:
    :type x1:
    :param y1:
    :type y1:
    :param x2:
    :type x2:
    :param y2:
    :type y2:
    :param radius:
    :type radius:
    :param radius1:
    :type radius1:
    :param radius2:
    :type radius2:
    :param radius3:
    :type radius3:
    :param radius4:
    :type radius4:
    :param kwargs:
    :type kwargs:
    :return:
    :rtype:
    """
    points = round_rectangle_points(x1, y1, x2, y2, radius, radius1, radius2, radius3, radius4)
    return canvas.create_polygon(points, **kwargs, smooth=True)


def round_rectangle_points(x1, y1, x2, y2, radius=25, radius1=None, radius2=None, radius3=None, radius4=None):
    """
    Returns points of rounded rectangle
    :param x1:
    :type x1:
    :param y1:
    :type y1:
    :param x2:
    :type x2:
    :param y2:
    :type y2:
    :param radius:
    :type radius:
    :param radius1:
    :type radius1:
    :param radius2:
    :type radius2:
    :param radius3:
    :type radius3:
    :param radius4:
    :type radius4:
    :return:
    :rtype:
    """
    if radius * 2 > (x2 - x1):
        radius = (x2 - x1 - 2) / 2

    radius1 = radius1 or radius
    radius2 = radius2 or radius
    radius3 = radius3 or radius
    radius4 = radius4 or radius

    points = [x1 + radius1, y1,
              x2 - radius2, y1,
              x2, y1,
              x2, y1 + radius2,
              x2, y2 - radius3,
              x2, y2,
              x2 - radius3, y2,
              x1 + radius4, y2,
              x1, y2,
              x1, y2 - radius4,
              x1, y1 + radius1,
              x1, y1]
    return points


def round_corner_points(x, y, w, h, radius=25):
    """
    Returns rounded corner points
    :param x:
    :type x:
    :param y:
    :type y:
    :param w:
    :type w:
    :param h:
    :type h:
    :param radius:
    :type radius:
    :return:
    :rtype:
    """
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
    """
    Returns rounded frame points
    :param x:
    :type x:
    :param y:
    :type y:
    :param w:
    :type w:
    :param h:
    :type h:
    :param radius:
    :type radius:
    :return:
    :rtype:
    """
    corners = []
    for i in range(4):
        points = round_corner_points(x - w / 2, y - h / 2, w / 2, h / 2, radius=radius)
        rotate_polygon(points, x, y, oz=i * -math.pi / 2)
        corners.append(points)
    return corners


class InputField(tk.Frame):
    def __init__(self, controller, canvas, x, y, w, h, text='', empty_text='', on_enter=None, bg='#ffffff',
                 font=('Colibri', 26), maxlen=-1, is_password=False, radius=25):
        tk.Frame.__init__(self, controller, highlightthickness=0)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.radius = radius
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
        self.coursor = 0
        self.own_canvas = False

        if canvas is None:
            self.own_canvas = True
            self.canvas = tk.Canvas(self, width=self.w, height=self.h, bg=self.bg, bd=-2, highlightthickness=0)
            self.canvas.bind("<Button-1>", self.clicked)
            self.x = 0
            self.y = 0
            self.canvas.pack()

    def hide(self):
        """
        Hides input field
        """
        self.canvas.delete(self.id)
        self.canvas.delete(self.id + '_text')

    def init_canvas(self):
        """
        Initialize elements on canvas
        """
        self.canvas.delete(self.id)
        self.canvas.delete(self.id + '_text')
        self.visible_text = self.text if not self.is_password else ('*' * self.text.__len__())
        self.canvasbg = self.canvas.create_polygon(
            round_rectangle_points(self.x * self.scale[0], self.y * self.scale[1], (self.x + self.w) * self.scale[0],
                                   (self.y + self.h) * self.scale[1], self.radius), smooth=True, fill=self.bg,
            tag=self.id)
        self.canvastext = self.canvas.create_text((self.x + self.text_padding) * self.scale[0],
                                                  (self.y + self.h / 2) * self.scale[1], text=self.visible_text,
                                                  anchor='w', tag=self.id + '_text',
                                                  font=self.font)
        self.update_text()

    def paste(self, e):
        print(e)

    def key(self, e):
        """
        Handles keypress
        :param e:
        :type e:
        :return:
        :rtype:
        """
        if self.in_focus:
            if e.keycode == 17:
                return
            if e.keycode == 8:
                self.text = self.text[:max(0, self.coursor - 1)] + self.text[self.coursor:]
                self.coursor = max(0, self.coursor - 1)
                self.update_text()
            elif e.keycode == 37:
                self.coursor = max(0, self.coursor - 1)
                self.update_text()
            elif e.keycode == 39:
                self.coursor = min(self.text.__len__(), self.coursor + 1)
                self.update_text()
            elif e.char == '\t' or e.char == '\n' or e.char == '\r' or e.char == '':
                print(self.text)
                self.in_focus = False
                if self.on_ener:
                    self.on_ener(self)
                self.update_text()
            elif self.maxlen < 0 or self.text.__len__() < self.maxlen:
                if e.char != '':
                    self.text = self.text[:self.coursor] + e.char + self.text[self.coursor:]
                    self.coursor = min(self.text.__len__(), self.coursor + 1)
                    self.update_text()

    def clicked(self, e):
        """
        Sets focus
        :param e:
        :type e:
        :return:
        :rtype:
        """
        elems = self.canvas.find_overlapping(e.x, e.y, e.x, e.y)
        if self.canvasbg in elems or self.canvastext in elems:
            if not self.in_focus:
                self.in_focus = True
                for i in range(10):
                    self.canvas.bind(i, self.key)
                self.canvas.bind('<Key>', self.key)
                self.canvas.bind('<<Cut>>', self.key)
                self.canvas.bind('<<Copy>>', self.key)
                self.canvas.bind('<<Paste>>', self.paste)
                self.canvas.focus_set()
                self.blink()
            return True
        else:
            self.in_focus = False
            return False

    def blink(self, t=False):
        """
        Cart blink
        :param t:
        :type t:
        :return:
        :rtype:
        """
        if self.in_focus:
            if self.focus_lastfor() != self.canvas:
                self.in_focus = False
                self.update_text()
                return
            if t:
                self.visible_text = self.text if not self.is_password else ('*' * self.text.__len__())
                self.visible_text = self.visible_text[:self.coursor] + '|' + self.visible_text[self.coursor:]
            else:
                self.visible_text = self.text if not self.is_password else ('*' * self.text.__len__())
                self.visible_text = self.visible_text[:self.coursor] + ' ' + self.visible_text[self.coursor:]
            self.canvas.itemconfigure(self.id + '_text', text=self.visible_text, font=self.font)
            self.controller.after(500, lambda: self.blink(t=not t))
        elif not t:
            self.update_text()

    def update_text(self):
        """
        Updates text on canvas
        """
        fill = '#224b79'
        if self.text == '':
            fill = '#91b0cf'
            self.visible_text = self.empty_text
        else:
            self.visible_text = self.text if not self.is_password else ('*' * self.text.__len__())

        self.font = fit_text((self.w - self.text_padding * 2) * self.scale[0], (self.h * 0.8) * self.scale[1],
                             self.visible_text + ' ' if self.maxlen < 0 else (
                                     self.visible_text + ' ' * (1 + self.maxlen - self.text.__len__())), self.font)

        self.canvas.itemconfigure(self.id + '_text', text=self.visible_text, font=self.font, fill=fill)

    def resize(self, w, h, aw, ah):
        self.scale = (aw, ah)
        if self.own_canvas:
            self.canvas.configure(width=self.w * aw, height=self.h * ah)
        self.init_canvas()


class Row(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.widgets = []

    def add(self, *widgets):
        """
        Adds widget to row
        :param widgets:
        :type widgets:
        """
        for widget in widgets:
            widget.grid(column=self.widgets.__len__(), row=0, sticky='n')
            self.widgets.append(widget)

    def resize(self, w, h, aw, ah):
        """
        Resizes elements of the row
        :param w:
        :type w:
        :param h:
        :type h:
        :param aw:
        :type aw:
        :param ah:
        :type ah:
        """
        for widget in self.widgets:
            widget.resize(w, h, aw, ah)


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
        """
        Adds widget to display
        :param widgets:
        :type widgets:
        """
        for widget in widgets:
            widget.grid(column=self.widgets.__len__(), row=0, sticky='n')
            self.widgets.append(widget)

    def resize(self, w, h, aw, ah):
        self.userscanvas.configure(height=self.h * ah, width=self.w * aw)
        self.scale = (aw, ah)
        self.rotate(self.a)

    def tapped(self, e):
        """
        Handles click
        :param e:
        :type e:
        """
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
            self.clicked(e, self.userscanvas, self.w, self.h, self.padding, self.scale, (self.a % 360) * math.pi / 180)

    def updatecanvas(self):
        self.rotate(self.a)
        self.update()

    def rotate(self, to):
        """
        Rotates figures on canvas
        :param to:
        :type to:
        """
        self.userscanvas.delete('rr')
        self.userscanvas.delete('img')
        self.userscanvas.delete('menuline')

        alpha = (self.a % 360) * math.pi / 180
        points = round_rectangle_points(self.padding * self.scale[0], self.padding * self.scale[1],
                                        (self.w - self.padding) * self.scale[0],
                                        (self.h - self.padding) * self.scale[1], radius=64)
        rotate_polygon(points, (self.w / 2) * self.scale[0], self.h / 2, oy=alpha)
        self.userscanvas.create_polygon(points, fill='#91b0cf', tag='rr', smooth=True)

        for i in range(3):
            points = round_rectangle_points((self.w * 0.85 - self.padding) * self.scale[0],
                                            (self.h / 10 + i * 8) * self.scale[1],
                                            (self.w * 0.95 - self.padding) * self.scale[0],
                                            (self.h / 10 + i * 8 + 3) * self.scale[1],
                                            )
            rotate_polygon(points, (self.w / 2) * self.scale[0], 0, oy=alpha)
            self.userscanvas.create_polygon(points, fill='#4978a6', tag='menuline', smooth=False)

        self.view(self.userscanvas, self.w, self.h, self.padding, self.scale, self.a)

        if self.a != to:
            self.a = (self.a + 5) % 360
            self.after(16, lambda: self.rotate(to))

class Note(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.pages = []
        self.current_index = -1

    def add(self, *widgets):
        """
        Adds page
        :param widgets:
        :type widgets:
        """
        self.pages += widgets

    def remove(self, page):
        """
        Removes page
        :param page:
        :type page:
        """
        if isinstance(page, int):
            del self.pages[page]
        else:
            for i in range(self.pages.__len__()):
                if self.pages[i] == page:
                    self.pages.remove(page)
                    break

    def select(self, page=None, previous=False, next=False):
        """
        Changes current page
        :param page:
        :type page:
        :param previous:
        :type previous:
        :param next:
        :type next:
        """
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
        self.pages[self.current_index].pack(expand=tk.YES, fill=tk.BOTH, padx=0, pady=0, side='top')

    def resize(self, w, h, aw, ah, all=False):
        """
        Resizes current page if all is False
        else resizes all pages
        :param w:
        :type w:
        :param h:
        :type h:
        :param aw:
        :type aw:
        :param ah:
        :type ah:
        :param all:
        :type all:
        """
        if all:
            for page in self.pages:
                if hasattr(page, 'resize'):
                    page.resize(w, h, aw, ah)
        elif hasattr(self.pages[self.current_index], 'resize'):
            self.pages[self.current_index].resize(w, h, aw, ah)


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvases = []
        self.canvases_to_resize = []
        self.last_scale = (1, 1)

    def xview(self, scroll, step):
        """
        moves canvases
        :param scroll:
        :type scroll:
        :param step:
        :type step:
        """
        for canvas in self.canvases:
            canvas.xview_moveto(step)

    def resize(self, w, h, aw, ah):
        self.last_scale = (aw / self.last_scale[0], ah / self.last_scale[1])

    def add_canvas(self, canvas):
        """
        Adds new canvas to scroll
        :param canvas:
        :type canvas:
        """
        if canvas in self.canvases:
            self.canvases.remove(canvas)
        self.canvases.append(canvas)
        canvas.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

    def remove_scrollableframe(self, frame):
        """
        Removes frame
        :param frame:
        :type frame:
        """
        if frame.master.master in self.canvases:
            frame.master.master.forget()
            self.canvases.remove(frame.master.master)
            self.canvases_to_resize.remove(frame.master.master)

    def get_scrollableframe(self, row=222, height=100):
        """
        Provides a scrollable frame for widgets
        :param row:
        :type row:
        :param height:
        :type height:
        :return:
        :rtype:
        """
        canvas = tk.Canvas(self, height=height, bg='#4978a6')
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.pack(side="top", fill="both", expand=True)
        self.canvases_to_resize.append(canvas)
        self.canvases.append(canvas)
        return scrollable_frame


class TableWidget(tk.Frame):
    def __init__(self, parent, data, w=550, h=400, fields=[], data_changed=None):
        tk.Frame.__init__(self, parent)
        self.w = w
        self.h = h
        self.data = data
        self.scrollList = None
        self.fields = fields
        self.available_fields = self.fields
        self.header = None
        self.indexes_to_load = (0, 0)
        self.loaded = True
        self.showing_setting = False
        self.ascending = True
        self.settings_container = None
        self.data_changed = data_changed
        self.horizontal_scrollbar = ScrollableFrame(self)
        self.horizontal_scrollbar.scrollbar = scrollbar = \
            HorizontalScrollBar(self.horizontal_scrollbar, w=w, car_w=w / 3,
                                callback=lambda a: self.horizontal_scrollbar.xview('moveto', a))
        scrollbar.pack(side="bottom", fill="x")
        self.horizontal_scrollbar_h = 30
        self.columns_on_screen = 3
        self.header_height = 40
        self.sort_field = 'id'
        self.choosable_fields = {}
        self.scale = (1, 1)
        self.load_thread = None
        self.everything_loaded = False
        self.selectedUsers = set()
        self.sorted_data = pd.DataFrame(None, columns=self.available_fields)
        self.input_row = Row(self)
        self.inputfield = inputfield = InputField(self.input_row, None, 0, 0, self.w - 6 * self.header_height,
                                                  self.header_height, text='', bg='#ffffff',
                                                  empty_text='Search',
                                                  on_enter=lambda a: self.search(a.text))
        inputfield.init_canvas()
        self.input_row.add(self.inputfield)
        add_new = SimpleButton(self.input_row, w=self.header_height, h=self.header_height, text='+',
                               onclicked=self.add_new, padding=5)
        self.input_row.add(add_new)
        check_all = SimpleButton(self.input_row, w=self.header_height, h=self.header_height, text='✓',
                                 onclicked=self.check_all, padding=5)
        self.input_row.add(check_all)
        uncheck_all = SimpleButton(self.input_row, w=self.header_height, h=self.header_height, text='☐',
                                   onclicked=self.uncheck_all, padding=5)
        self.input_row.add(uncheck_all)

        delete_checked = SimpleButton(self.input_row, w=self.header_height, h=self.header_height, text='✗',
                                      onclicked=self.delete_checked, padding=5)
        self.input_row.add(delete_checked)
        show_settings = SimpleButton(self.input_row, w=self.header_height, h=self.header_height, text=chr(9881),
                                     onclicked=self.show_settings, padding=5, fixed=True)
        self.input_row.add(show_settings)
        save_table = SimpleButton(self.input_row, w=self.header_height, h=self.header_height, text="S",
                                  onclicked=self.save_base, padding=5, fixed=True)
        self.input_row.add(save_table)
        self.input_row.grid(row=0, column=0, sticky='n')
        # inputfield.grid(row=0, column=0, sticky='n')
        self.init_table()
        self.setup_search('')
        self.loadedIndexes = (0, 0)
        self.init_load(0, 50)


    def save_base(self):
        """
        Saves data to csv file
        """
        if self.data is not None and self.data.__len__():
            filePath = tk.filedialog.asksaveasfile(mode='w', defaultextension=".csv")
            if filePath:
                self.data.to_csv(filePath, encoding='utf-8', )

    def make_search_sequence(self):
        """
        Makes search sequence from selected fields in settings
        """
        for child in self.settings_container.children.values():
            if isinstance(child, Row):
                if '!inputfield' in child.children and '!simplebutton' in child.children and child.children[
                    '!inputfield'].text != '':
                    if self.search_sequence != '':
                        self.search_sequence += ' and '
                    self.search_sequence += '(' + child.children['!simplebutton'].text + '==\'' + child.children[
                        '!inputfield'].text + '\')'

            elif isinstance(child, RadioButton):
                field = child.header.text
                selected = child.get_selected()
                if selected.__len__() > 0:
                    if self.search_sequence != '':
                        self.search_sequence += ' and '
                    self.search_sequence += '('
                    for value in selected:
                        self.search_sequence += field + '==\'' + str(value) + '\' or '
                    self.search_sequence = self.search_sequence[:-3] + ')'
        self.inputfield.text = self.search_sequence
        self.search_sequence = self.format_sequence(self.search_sequence)
        self.inputfield.update_text()
        self.settings_container = None
        self.search(self.search_sequence)

    def format_sequence(self, sequence):
        """
        checks search_sequence and fixes mistakes
        :param sequence:
        :type sequence:
        :return:
        :rtype:
        """
        return sequence
        result = []
        current_field = ''
        operators = [
            '>=', '<=', '==', '=',
            '&&', ','
                  '||',
            '//',
            '%',
            '\+', '\-', '\*', '\/',
        ]
        fields = {}
        # 0 - expect var, 1 - expect compare or op, 2 - expect op or separator
        step = 0
        seq_list = list(
            filter(lambda a: a is not None and a != '' and a != ' ', re.split('|'.join(operators), sequence)))
        for op in seq_list:
            if op == '>=' or op == '<=' or op == '>' or op == '<' or op == '==' or op == '=':
                if step == 1:
                    step = 2
                    result.append(op)
                else:
                    result = None
                    break
            if op == '&&' or op == ' and ' or op == 'и' or op == ',':
                if step == 2:
                    result.append(' and ')
                else:
                    result = None
                    break
            elif op == '||' or op == ' or ' or op == 'или':
                if step == 2:
                    result.append(' or ')
                result = None
                break
            elif op == 'in' or op == 'в':
                if got_op:
                    continue
                result += ' in '
            elif op == ' div ' or op == '//':
                if got_op:
                    continue
                result.append(' // ')
            elif op == ' mod ' or op == '%':
                if got_op:
                    continue
                result.append(' % ')
            elif op == '+' or op == '-' or op == '*' or op == '/':
                if got_op:
                    continue
                result.append(op)
            else:
                if not got_op and result.__len__() > 0:
                    del result[-1]
                result.append(op)

        return sequence

    def show_edit(self, item):
        """
        Show edit window
        :param item:
        :type item:
        """
        w = self.w * 2 / 3 * self.scale[0]
        h = self.h * 2 / 3 * self.scale[1]
        self.scrollList.textcolor = '#aaaaaa'
        for button in self.scrollList.buttons:
            button.textcolor = self.scrollList.textcolor
            button.needsupdate = True
        self.scrollList.updatecanvas()
        container = tk.Frame(self, highlightbackground="#4978a6", highlightcolor="#4978a6",
                             highlightthickness=5)
        header_template = SimpleButton(self, text='ht', w=w / 4, h=h / (self.fields.__len__() - 1), borderradius=0,
                                       padding=2,
                                       fillcolor='#4978a6')
        counter = 0
        for field in self.available_fields:
            if field == 'id' and item is not None:
                continue
            if field == 'region' and item is None:
                continue
            row = Row(container)
            if item is not None:
                val = self.data.loc[self.data['id'] == item.value, field]
            else:
                val = ''
            if not isinstance(val, pd.Series) or len(val) == 0:
                val = ""
            else:
                val = val.item()
            if pd.isna(val):
                val = ""
            else:
                if field == 'city':
                    val = get_city_by_id(val)
                else:
                    val = str(val)
            simple_button = SimpleButton(
                row,
                w=header_template.w,
                h=header_template.h,
                backgroundcolor=header_template.backgroundcolor,
                onclicked=None, text=field, icon=None, textcolor=header_template.textcolor,
                fillcolor=header_template.fillcolor, loadcolor=header_template.loadcolor,
                borderradius=header_template.borderradius,
                padding=header_template.padding, font=header_template.font
            )
            row.add(simple_button)
            inputfield = InputField(row, None, 0, 0, (w - header_template.w),
                                    header_template.h, text=val, bg='#ffffff',
                                    empty_text='',
                                    on_enter=None, radius=2)
            inputfield.init_canvas()
            row.add(inputfield)
            row.grid(row=counter, column=0)
            counter += 1
        row = Row(container)
        button_save = SimpleButton(row, text='Save', w=60, h=20, borderradius=4, padding=4,
                                   onclicked=lambda: self.save_changes(container, -1 if item is None else item.value))
        button_discard = SimpleButton(row, text='Discard', w=60, h=20, borderradius=4, padding=4,
                                      onclicked=lambda: self.discard_changes(container))
        row.add(button_save)
        row.add(button_discard)
        row.grid(row=counter, column=0)
        container.grid(row=1, column=0)
        self.update()

    def save_changes(self, container, id):
        """
        Saves changes after edit and closes the window
        :param container:
        :type container:
        :param id:
        :type id:
        :return:
        :rtype:
        """
        for child in container.children.values():
            if isinstance(child, Row):
                if '!inputfield' in child.children and '!simplebutton' in child.children:
                    if not child.children['!simplebutton'].text in self.data.columns:
                        continue
                    t = self.data[child.children['!simplebutton'].text].dtype
                    if child.children['!simplebutton'].text == 'id':
                        try:
                            id = int(child.children['!inputfield'].text)
                            if id <= 0: raise ValueError
                        except ValueError:
                            child.children['!inputfield'].bg = '#ffadad'
                            child.children['!inputfield'].init_canvas()
                            return
                        self.data = self.data.append(pd.Series(
                            {'id': id}), ignore_index=True)

                    if t.kind != 'O' and t.kind != 'S' and t.kind != 'U' and not child.children[
                        '!inputfield'].text.isnumeric():
                        if child.children['!simplebutton'].text == 'city':
                            if child.children['!inputfield'].text:
                                city_id = get_id_by_city(child.children['!inputfield'].text)
                                if city_id > 0:
                                    self.data.loc[self.data['id'] == id, child.children['!simplebutton'].text] = city_id
                                else:
                                    child.children['!inputfield'].bg = '#ffadad'
                                    child.children['!inputfield'].init_canvas()
                                    return
                            else:
                                self.data.loc[self.data['id'] == id, child.children['!simplebutton'].text] = 0
                        else:
                            self.data.loc[self.data['id'] == id, child.children['!simplebutton'].text] = 0
                    else:
                        self.data.loc[self.data['id'] == id, child.children['!simplebutton'].text] = child.children[
                            '!inputfield'].text
                    self.data[child.children['!simplebutton'].text] = self.data[
                        child.children['!simplebutton'].text].astype(t)

        container.grid_forget()
        self.scrollList.textcolor = '#224b79'
        self.scrollList.updatecanvas()
        self.update()
        self.search(self.search_sequence)

    def discard_changes(self, container):
        """
        Closes edit window
        :param container:
        :type container:
        """
        container.grid_forget()
        self.scrollList.textcolor = '#224b79'
        for button in self.scrollList.buttons:
            button.textcolor = self.scrollList.textcolor
            button.needsupdate = True
        self.scrollList.updatecanvas()
        self.update()

    def closeSettings(self):
        """
        Closes settings window
        """
        self.settings_container.grid_forget()
        self.scrollList.textcolor = '#224b79'
        self.scrollList.updatecanvas()
        self.update()

    def show_settings(self):
        """
        Show settings window
        :return:
        :rtype:
        """
        w = self.w * 2 / 3 * self.scale[0]
        h = self.h * 2 / 3 * self.scale[1]
        if self.settings_container:
            for c in self.settings_container.children.values():
                if '!simplebutton' in c.children and c.children['!simplebutton'].text == 'city':
                    if c.children['!inputfield'].text:
                        city_id = get_id_by_city(c.children['!inputfield'].text)
                        if city_id > 0:
                            c.children['!inputfield'].text = str(city_id)
                        elif not c.children['!inputfield'].text.isnumeric():
                            c.children['!inputfield'].bg = '#ffadad'
                            c.children['!inputfield'].init_canvas()
                            return

            self.settings_container.grid_forget()
            self.scrollList.textcolor = '#224b79'
            self.search_sequence = ''
            th.Thread(target=lambda: self.make_search_sequence(), daemon=True).start()
            for button in self.scrollList.buttons:
                button.textcolor = self.scrollList.textcolor
                button.needsupdate = True
            # self.scrollList.initcanvas()
            self.scrollList.updatecanvas()
            self.update()
            return
        self.scrollList.textcolor = '#aaaaaa'
        for button in self.scrollList.buttons:
            button.textcolor = self.scrollList.textcolor
            button.needsupdate = True
        # self.scrollList.initcanvas()
        self.scrollList.updatecanvas()
        self.settings_container = container = tk.Frame(self, highlightbackground="#4978a6", highlightcolor="#4978a6",
                                                       highlightthickness=5)
        header_template = SimpleButton(self, text='ht', w=w / 4, h=h / self.fields.__len__(), borderradius=0, padding=2,
                                       fillcolor='#4978a6')
        child_template = SimpleButton(self, text='ht', w=60, h=h / self.fields.__len__(), borderradius=4, padding=4)
        counter = 0
        for field in self.available_fields:
            if field in self.choosable_fields:
                child_template.w = (w - header_template.w) / self.choosable_fields[field].__len__()
                rb = RadioButton(container, header_template=header_template, child_template=child_template,
                                 can_choose_multiple=True)
                rb.set_header(field)
                for value in self.choosable_fields[field]:
                    rb.add_value(value)
                rb.grid(row=counter, column=0)
            else:
                row = Row(container)
                simple_button = SimpleButton(
                    row,
                    w=header_template.w,
                    h=header_template.h,
                    backgroundcolor=header_template.backgroundcolor,
                    onclicked=None, text=field, icon=None, textcolor=header_template.textcolor,
                    fillcolor=header_template.fillcolor, loadcolor=header_template.loadcolor,
                    borderradius=header_template.borderradius,
                    padding=header_template.padding, font=header_template.font
                )
                row.add(simple_button)
                inputfield = InputField(row, None, 0, 0, (w - header_template.w),
                                        header_template.h, text='', bg='#ffffff',
                                        empty_text='',
                                        on_enter=None, radius=2)
                inputfield.init_canvas()
                row.add(inputfield)
                row.grid(row=counter, column=0)
            counter += 1
        container.grid(row=1, column=0)
        self.update()

    def add_new(self):
        self.show_edit(None)

    def check_all(self):
        """
        Selects all rows that satisfy settings
        """
        data = self.data.query(self.search_sequence, engine='python')
        self.selectedUsers.update(set(data['id'].values.tolist()))
        self.sort(self.sort_field)

    def uncheck_all(self):

        data = self.data.query(self.search_sequence, engine='python')
        data = data.query('id in @self.selectedUsers')['id'].values.tolist()
        for id in data:
            if id in self.selectedUsers:
                self.selectedUsers.remove(id)
        self.sort(self.sort_field)

    def delete_checked(self):
        """
        Deletes chosen rows
        """
        self.data = self.data.query('not (id in @self.selectedUsers)')
        if self.data_changed:
            self.data_changed(self.data)
        self.sort(self.sort_field)

    def init_header(self, fields):
        """
        Inits header
        :param fields:
        :type fields:
        """
        if self.header:
            self.header.pack_forget()
            self.horizontal_scrollbar.remove_scrollableframe(self.header)
        frame = self.horizontal_scrollbar.get_scrollableframe(height=self.header_height)
        self.header = row = RadioButton(frame,
                                        child_template=SimpleButton(self,
                                                                    w=round(self.w / self.columns_on_screen),
                                                                    h=self.header_height,
                                                                    borderradius=0, padding=0),
                                        onclicked=lambda a: self.sort(a[0]))
        for field in fields:
            row.add_value(field)
        row.pack()

    def item_clicked(self, item):
        """
        Handles click (adds to chosen)
        :param item:
        :type item:
        :return:
        :rtype:
        """
        if not isinstance(item, WideScrollListButton):
            return
        if item.isChosen:
            self.selectedUsers.add(item.value)
        elif item.value in self.selectedUsers:
            self.selectedUsers.remove(item.value)
        print(self.selectedUsers)

    def item_dblclicked(self, item):
        """
        Handles doubleclick (shows edit text)
        :param item:
        :type item:
        :return:
        :rtype:
        """
        if not isinstance(item, WideScrollListButton):
            return
        self.show_edit(item)

    def init_table(self):
        """
        Inits base elements
        """
        self.init_header(self.fields)
        self.scrollList = ScrollList(self.horizontal_scrollbar, choosable=True, loadcolor='#91b0cf',
                                     pointerup=self.pointerup,
                                     pointerdown=self.pointerdown, moved=self.moved, padding=(0, 0, 6, 0),
                                     w=self.w,
                                     h=self.h - self.header_height - self.inputfield.h - self.horizontal_scrollbar.scrollbar.h,
                                     fillcolor='white', borderradius=0, textcolor='#224b79', item_height=20,
                                     item_padding=5, onclicked=self.item_clicked, ondblclicked=self.item_dblclicked)
        self.scrollList.pack(side='bottom', expand=False, fill='x')
        self.horizontal_scrollbar.add_canvas(self.scrollList.canvas)
        self.horizontal_scrollbar.grid(column=0, row=1, columnspan=1, sticky='nsew')

    def getLambda(self, foo, arg):
        return lambda: foo(arg.encode().decode())

    def fill_scroll_lists(self, data, a=0, b=6):
        """
        Fills table
        :param data:
        :type data:
        :param a:
        :type a:
        :param b:
        :type b:
        """
        available_fields = []
        if self.fields.__len__() == 0:
            self.fields = data.columns
        for field in self.fields:

            if field in data.columns:
                available_fields.append(field)
        if set(available_fields).difference(self.available_fields).__len__() > 0 or True:
            self.available_fields = available_fields
            self.init_header(self.available_fields)
        for _, row in data[available_fields].iterrows():
            if row['followers_count'] == -1:
                row['followers_count'] = ' '
            row['city'] = get_city_by_id(row['city'])
            if row['graduation'] < 1:
                row['graduation'] = ''

            wide_button = WideScrollListButton(
                tag='',
                y=0, values=row['id'], text=row.values, fillcolor=self.scrollList.fillcolor,
                choosable=self.scrollList.choosable, borderradius=self.scrollList.borderraadius,
                loadcolor=self.scrollList.loadcolor, textcolor=self.scrollList.textcolor, parts=self.columns_on_screen,
                step=self.scrollList.w / self.columns_on_screen
            )
            if wide_button.value in self.selectedUsers:
                wide_button.isChosen = True
            self.scrollList.add(wide_button, update=False)

        self.loadedIndexes = (0, self.scrollList.buttons.__len__())
        print('Filled ', self.loadedIndexes)

    def pointerdown(self, e):
        """
        pointerdown wrapper
        :param e:
        :type e:
        """
        self.inputfield.in_focus = False
        self.scrollList.pointerdown(e)

    def pointerup(self, e):
        """
        pointerup wrapper
        :param e:
        :type e:
        """
        self.scrollList.pointerup(e)

    def moved(self, e):
        """
        handles drags
        :param e:
        :type e:
        """
        self.scrollList.moved(e)
        self.scrollList.updatecanvas()
        visibleIndexes = self.scrollList.getVisibleIndexes()
        if self.loadedIndexes[1] < visibleIndexes[1] + 5 and self.loaded and not self.everything_loaded:
            self.loaded = False
            self.init_load(self.loadedIndexes[1], self.loadedIndexes[1] + 50)

    def update_header(self):
        """
        Shows sort field and order
        """
        for button in self.header.values:
            if button.text == self.sort_field or button.text[:-1] == self.sort_field:
                button.text = self.sort_field + ('↑' if self.ascending else '↓')
                button.updatecanvas()
            elif button.text.endswith('↓') or button.text.endswith('↑'):
                button.text = button.text[:-1]
                button.updatecanvas()

    def setup_sort(self, field):
        """
        Setups sort field and order
        :param field:
        :type field:
        """
        if field.endswith('↓') or field.endswith('↑'):
            field = field[:-1]
        self.sort_field = field
        self.ascending = not self.ascending

    def sort(self, field):
        """
        Sorts data and updates scrollist
        :param field:
        :type field:
        """
        self.setup_sort(field)
        self.scrollList.reset()
        self.everything_loaded = False
        self.loadedIndexes = (0, 0)
        self.init_load(0, 50)

    def resize(self, w, h, aw, ah):
        """
        Resizes widget
        :param w:
        :type w:
        :param h:
        :type h:
        :param aw:
        :type aw:
        :param ah:
        :type ah:
        """
        self.scale = (aw, ah)
        self.horizontal_scrollbar.resize(w, h, aw, ah)
        self.input_row.resize(w, h / ah, aw, 1)
        self.scrollList.resize(w, h, aw, (
                self.h * ah - self.header_height - self.inputfield.h - self.horizontal_scrollbar.scrollbar.h) / self.scrollList.h,
                               only_canvas=True
                               )
        self.horizontal_scrollbar.scrollbar.resize(w, h, aw, ah)
        self.update()

    def setup_search(self, seq):
        """
        Setups search sequence
        :param seq:
        :type seq:
        """
        self.search_sequence = self.format_sequence(seq)
        if self.search_sequence == '':
            self.search_sequence = 'tuple()'

    def search(self, seq):
        """
        Makes search and updates scrolllist
        :param seq:
        :type seq:
        """
        self.setup_search(seq)
        self.scrollList.reset()
        self.everything_loaded = False
        self.loadedIndexes = (0, 0)
        self.init_load(0, 50)
        self.inputfield.empty_text = seq if seq != '' else 'Search:'

    def init_load(self, a, b):
        """
        Shows progressbar and fills scrollist
        :param a:
        :type a:
        :param b:
        :type b:
        :return:
        :rtype:
        """
        if self.load_thread:
            return
        self.load_thread = thread = th.Thread(target=self.load_data, args=([self.sort_field, self.ascending, a, b]),
                                              daemon=True)
        thread.start()
        self.loadCanvas = canvas = tk.Canvas(self, width=self.w, height=self.h - 30)
        canvas.configure(bg='#f1f0ec')
        self.progressBar = ProgressBar(self, canvas, 550 / 2, 400 / 2, 40, 60, '#91b0cf', '#224b79')
        self.progressBar.working = True
        self.progressBar.drawprogress()
        canvas.grid(column=0, row=1, columnspan=1, sticky='nsew')
        self.wait_for_load()

    def wait_for_load(self):
        """
        Shows scrollbar
        """
        if self.loaded:
            self.load_thread.join()
            print('Load complete')
            self.progressBar.working = False
            self.loadCanvas.grid_forget()
            self.scrollList.updatecanvas()
            self.update_header()
            print(self.loadedIndexes)
            self.sorted_data = None
            self.load_thread = None
            self.horizontal_scrollbar.add_canvas(self.scrollList.canvas)
            self.horizontal_scrollbar.scrollbar.set_progress(0)
            self.horizontal_scrollbar.scrollbar.updatecanvas()
            self.horizontal_scrollbar.xview('', 0)
            self.update()
        else:
            self.after(500, self.wait_for_load)

    def load_data(self, field, ascending, a, b):
        """
        Loads data and fills scrolllist
        :param field:
        :type field:
        :param ascending:
        :type ascending:
        :param a:
        :type a:
        :param b:
        :type b:
        """
        self.loaded = False
        if self.data.__len__() > 0:
            try:
                d = self.data.query(self.search_sequence, engine='python', ).sort_values(by=[field],
                                                                                         ascending=ascending)
            except Exception as e:
                print(e)
            else:
                self.sorted_data = d[a:b]
                self.fill_scroll_lists(self.sorted_data, a=a, b=b)
                self.choosable_fields = {}
                for column in self.data.columns:
                    values = self.data[column]
                    try:
                        values = values.unique()
                    except Exception as e:
                        print(e)
                    else:
                        if values.__len__() < 5:
                            self.choosable_fields[column] = values
                            print(values)
                if self.sorted_data.__len__() < b - a:
                    self.everything_loaded = True
        self.loaded = True


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

    def map_hover(self, details, updateScrollList=True):
        """
        Handles mouse hover
        :param details:
        :type details:
        :param updateScrollList:
        :type updateScrollList:
        """
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
        """
        Colors the map
        :param regions:
        :type regions:
        :param color_gradient:
        :type color_gradient:
        """
        self.minreg = 999999
        self.maxreg = -99

        for reg in regions:
            self.minreg = min(self.minreg, regions[reg])
            self.maxreg = max(self.maxreg, regions[reg])

        if self.minreg == self.maxreg:
            self.maxreg += 1

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
        """
        Draws polygons on canvas
        :param c:
        :type c:
        :param scale:
        :type scale:
        """
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
    scale = min(wscale, hscale)
    canvas.scale("all", 0, 0, scale, scale)


def getPolygons(s, scale=1.0, offsetX=0, offsetY=0):
    """
    Returns polygon points from polygon string
    :param s:
    :type s:
    :param scale:
    :type scale:
    :param offsetX:
    :type offsetX:
    :param offsetY:
    :type offsetY:
    :return:
    :rtype:
    """
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
    """
    Builds bezue curve from points
    :param points_in:
    :type points_in:
    :return:
    :rtype:
    """
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
    """
    Adjustes text size to fit given size
    :param w:
    :type w:
    :param h:
    :type h:
    :param text:
    :type text:
    :param font:
    :type font:
    :return:
    :rtype:
    """
    canvas = tk.Canvas()
    ctext = canvas.create_text(100, 100, text=text, font=font)
    box = canvas.bbox(ctext)
    while ((box[2] - box[0] > w or (box[3] - box[1]) > h) and font[1] > 1):
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
    """
    Rotates points
    :param points:
    :type points:
    :param x:
    :type x:
    :param y:
    :type y:
    :param ox:
    :type ox:
    :param oy:
    :type oy:
    :param oz:
    :type oz:
    """
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


def get_city_by_id(id):
    """
    Returns city name by id
    :param id:
    :type id:
    :return:
    :rtype:
    """
    global CITIES
    if CITIES is None:
        import configparser
        config = configparser.ConfigParser()
        config.read("Data/settings.ini")
        CITIES = pd.read_json(config['paths']['cities'], orient='index')
        CITIES = CITIES.drop(columns=['id', 'important'])
        CITIES = CITIES.append(pd.Series({'title': 'Москва', 'area': 'Москва', 'region': 'RU-MOS'}, name=1))
        CITIES = CITIES.append(
            pd.Series({'title': 'Санкт-Петербург', 'area': 'Санкт-Петербург', 'region': 'RU-SPB'}, name=2))

    if id in CITIES.index:
        return CITIES.loc[id]['title']
    return ''


def get_id_by_city(city):
    """
    returns id from city name
    :param city:
    :type city:
    :return:
    :rtype:
    """
    if CITIES is None:
        get_city_by_id(0)
    r = CITIES[CITIES['title'] == city].index
    if r.__len__():
        return r[0]
    else:
        return -1
