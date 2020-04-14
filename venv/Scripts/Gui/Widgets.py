import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
    def __init__(self, parent, w=400, h=50, backgroundcolor='#4978a6', onclicked=(), pages=[], textcolor='#cadef7',
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
        c.pack()
        self.canvas = c
        self.initcanvas()

    def initcanvas(self):
        # self.round_rectangle(self.padding, self.padding, self.w - self.padding, self.h - self.padding, radius=self.borderraadius,  outline=self.fillcolor, fill=self.fillcolor)
        x = self.padding
        self.buttons = []
        self.canvas.delete('all')

        for i in range(self.pages.__len__()):
            if self.currentPage == i:
                print(i)
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
                    self.initcanvas()
                    break


class ScrollList(tk.Frame):
    def __init__(self, parent, w=BUTTON_WIDTH + 2 * PADDING, h=(BUTTON_HEIGHT + PADDING) * 4 + PADDING / 2,
                 bg='#f1f0ec', onclicked=(), items=[], textcolor='#ffffff', figurecolor = None,
                 borderradius=18, fillcolor='#91b0cf', loadcolor='#224b79', padding=PADDING, item_padding = PADDING, item_height=BUTTON_HEIGHT):
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
        self.currentPage = 0
        self.padding = padding
        self.item_height = item_height
        self.item_padding = item_padding
        c = tk.Canvas(self, width=w, height=h, bg=bg, bd=-2)
        c.bind("<Button-1>", self.pointerdown)
        c.bind("<B1-Motion>", self.moved)
        c.bind("<ButtonRelease-1>", self.pointerup)
        c.pack()
        if not figurecolor is None:
            round_rectangle(c, padding/2, padding/2, w-padding/2, h-padding/2, radius = 32, fill=figurecolor)
        self.canvas = c
        self.dy = 0
        self.items = []
        self.buttons = []
        for item in items:
            self.add(item)

        self.visibleheight = min(self.h - self.items.__len__() * (self.item_height + self.padding), 0)
        self.initcanvas()

    def add(self, element):
        self.items.append(element)
        self.buttons.append(
            {'tag': 'item' + str(self.nextTag), 'y': None, 'text': element, 'font': "Colibri", 'fontsize': 25,
             'progress': 0.0, 'fillcolor': self.fillcolor, 'particles': []})
        self.nextTag += 1
        canvas = tk.Canvas(self)
        text = canvas.create_text(100, 100, text=element, font=(self.buttons[-1]['font'], self.buttons[-1]['fontsize']))
        box = canvas.bbox(text)
        while (box[2] - box[0] > self.w - 3 * self.padding or box[3] - box[1] > self.item_height - 1):
            self.buttons[-1]['fontsize'] -= 1
            text = canvas.create_text(100, 100, text=element,
                                      font=(self.buttons[-1]['font'], self.buttons[-1]['fontsize']))
            box = canvas.bbox(text)
        self.visibleheight = min(self.h - self.items.__len__() * (self.item_height + self.padding), 0)
        self.initcanvas()

    def remove(self, i=-1, button=None, name='', stage=0):
        # print('removing  ', button['text'])
        if i > -1:
            if stage == 0:
                self.remove_animation(self.buttons[i])
            else:
                self.canvas.delete(self.buttons[i]['tag'])
                self.canvas.delete(self.buttons[i]['tag']+'text')
                self.buttons.remove(i)
        elif button != None:
            if stage == 0:
                self.remove_animation(button)
            else:
                self.canvas.delete(button['tag'])
                self.canvas.delete(button['tag']+'text')
                self.buttons.remove(button)
        else:
            for button in self.buttons:
                if button['text'] == name:
                    if stage == 0:
                        self.remove_animation(button)
                    else:
                        self.canvas.delete(button['tag'])
                        self.canvas.delete(button['tag'] + 'text')
                        self.buttons.remove(button)
                    break
        self.initcanvas()

    def remove_animation(self, button, stage=0):
        button['progress'] = 0
        if stage < 10:
            by = stage / 10 * self.item_height
            button['particles'] += [
                [self.padding, by, self.w - self.padding, by + 10],

            ]
            self.after(100, lambda: self.remove_animation(button=button, stage=stage + 1))
        else:
            self.remove(button=button, stage=1)

    def initcanvas(self):
        y = self.dy + self.item_padding
        self.canvas.delete('progress')
        for i in range(self.buttons.__len__()):
            if y > self.h:
                break
                # state = 'normal' if self.buttons[i]['progress'] > 0 else 'hidden'
            itemparts = self.canvas.find_withtag((self.buttons[i]['tag']))
            if itemparts.__len__() > 0:
                for part in itemparts:
                    self.canvas.move(part, 0, y - self.buttons[i]['y'])
                text = self.canvas.find_withtag(self.buttons[i]['tag'] + 'text')
                self.canvas.move(text, 0, y - self.buttons[i]['y'])

                if self.buttons[i]['progress'] > 0:
                    round_rectangle(self.canvas, self.padding, y, (self.w - self.padding) * self.buttons[i]['progress'],
                                    y + self.item_height,
                                    radius=self.borderraadius, outline=self.loadcolor, fill=self.loadcolor,
                                    tag='progress')
                    self.canvas.tag_raise(text)

            else:
                print('new!')
                round_rectangle(self.canvas, self.padding, y, self.w - self.padding, y + self.item_height,
                                radius=self.borderraadius, outline=self.buttons[i]['fillcolor'],
                                fill=self.buttons[i]['fillcolor'], tag=self.buttons[i]['tag'])
                if self.buttons[i]['progress'] > 0:
                    round_rectangle(self.canvas, self.padding, y, (self.w - self.padding) * self.buttons[i]['progress'],
                                    y + self.item_height,
                                    radius=self.borderraadius, outline=self.loadcolor, fill=self.loadcolor,
                                    tag='progress')
                self.canvas.create_text(self.w / 2, y + self.item_height / 2, text=str(self.buttons[i]['text']),
                                        fill=self.textcolor,
                                        font=(self.buttons[i]['font'], self.buttons[i]['fontsize']),
                                        tag=self.buttons[i]['tag']+'text')

                # for particle in self.buttons[i]['particles']:
                #     self.canvas.create_rectangle(particle[0], particle[1], particle[2], particle[3], fill=self.backgroundcolor, outline=self.backgroundcolor)

            self.buttons[i]['y'] = y
            y += (self.item_height + self.item_padding)

        self.update()

    def pointerup(self, e):
        if ((e.x - self.pointerx) == 0 and (
                e.y - self.pointery) == 0 and e.y > self.padding and e.y < self.w - self.padding):
            for i in range(self.buttons.__len__()):
                if (e.y >= self.buttons[i]['y'] and e.y <= self.buttons[i]['y'] + self.item_height):
                    return

        if self.dy == self.padding / 2:
            self.dy = 0
            self.initcanvas()
        elif self.dy == self.visibleheight - self.padding / 2:
            self.dy = self.visibleheight
            self.initcanvas()

        # self.lasty = 0
        # self.pointerx = 0
        # self.pointery = 0
        # self.initcanvas()

    def pointerdown(self, e):
        self.pointerx = e.x
        self.pointery = e.y
        self.lasty = e.y

    def moved(self, d):
        ndy = d.y - self.lasty
        # self.dy = self.dy + ndy
        print(ndy, '  ', self.dy + ndy, '  ',
              min(self.padding / 2, self.dy + ndy) if ndy > 0 else max(self.dy + ndy, self.visibleheight), '  ',
              self.buttons[0]['y'], '   ', self.visibleheight)
        self.dy = min(self.padding / 2, self.dy + ndy) if ndy > 0 else max(self.dy + ndy,
                                                                           self.visibleheight - self.padding / 2)

        self.initcanvas()
        self.lasty = d.y

    def setProgress(self, i=-1, name='', progress=0):
        if i > -1:
            self.buttons[i]['progress'] = progress
            if progress >= 1:
                self.after(1000, lambda: self.remove(i=i, stage=1))
        else:
            for button in self.buttons:
                if button['text'] == name:
                    button['progress'] = progress
                    if progress >= 1:
                        # print('set progress ',name)
                        self.after(1000, lambda: self.remove(button=button, stage=1))
                    break
        self.initcanvas()


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
        c = tk.Canvas(self, width=w, height=h, bg=backgroundcolor)
        c.bind("<Button-1>", self.clicked)
        c.pack()
        self.canvas = c
        self.initcanvas()

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

    def initcanvas(self):
        self.canvas.delete('all')
        round_rectangle(self.canvas, self.padding, self.padding, self.w - self.padding, self.h - self.padding,
                        radius=self.borderradius, outline=self.fillcolor, fill=self.fillcolor)
        # self.canvas.create_rectangle(0, 0, prorgess / 100 * self.w, self.h, outline=self.backgroundcolor, fill=self.backgroundcolor)
        self.canvas.create_text(self.w / 2, self.h / 2, text=self.text, fill=self.textcolor, font=self.font)

    def drawProgress(self, prorgess):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, prorgess / 100 * self.w, self.h, outline=self.fillcolor, fill=self.fillcolor)
        if prorgess < 100:
            self.canvas.create_text(self.w / 2, self.h / 2, text=str(math.floor(prorgess)) + '%', fill=self.textcolor)
        else:
            self.canvas.create_text(self.w / 2, self.h / 2, text=str('done!'), fill=self.textcolor)
            self.after(1000, self.initcanvas)

    def watch_progress(self, progress):
        if progress.__len__() == 2:
            self.drawProgress(progress[0] / progress[1] * 100)
        else:
            self.drawProgress(progress[0])
        self.after(500, lambda: self.watch_progress(progress))


class SimpleButton(tk.Frame):

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
        c = tk.Canvas(self, width=w, height=h, bg=backgroundcolor)
        c.bind("<Button-1>", self.clicked)
        c.pack()
        self.canvas = c
        self.initcanvas(self.fillcolor)

    def clicked(self, e):
        self.initcanvas(self.loadcolor)
        self.onclicked()
        self.initcanvas(self.fillcolor)

    def initcanvas(self, color=None):
        self.canvas.delete('all')
        color = self.fillcolor if color is None else color
        round_rectangle(self.canvas, self.padding, self.padding, self.w - self.padding, self.h - self.padding,
                        radius=self.borderradius, outline=color, fill=color)
        self.canvas.create_text(self.w / 2, self.h / 2, text=self.text, fill=self.textcolor, font=self.font)


def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = round_rectangle_points(x1, y1, x2, y2, radius)
    return canvas.create_polygon(points, **kwargs, smooth=True)


def round_rectangle_points(x1, y1, x2, y2, radius=25):
    points = [x1 + radius, y1,
              # x1 + radius, y1,
              # x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              # x2, y1 + radius,
              # x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              # x2 - radius, y2,
              # x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              # x1, y2 - radius,
              # x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]
    return points
