import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math

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
        c.pack()
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
                 borderradius=18, fillcolor='#91b0cf', loadcolor='#224b79',
                 padding=(PADDING, PADDING, PADDING, PADDING), item_padding=PADDING,
                 item_height=BUTTON_HEIGHT, item_width=None, progress_offset=0):
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
        self.currentPage = 0
        self.progress_offset = progress_offset
        self.padding = (padding, padding, padding, padding) if isinstance(padding, int) or isinstance(padding,
                                                                                                      float) else (
            (padding[0], padding[1], padding[0], padding[1]) if padding.__len__() == 2 else padding)
        self.item_height = item_height
        self.item_width = item_width or self.w - self.padding[1] - self.padding[3]
        self.item_padding = item_padding
        c = tk.Canvas(self, width=w, height=h, bg=bg, bd=-2)
        c.bind("<Button-1>", self.pointerdown)
        c.bind("<B1-Motion>", self.moved)
        c.bind("<MouseWheel>", self.moved)
        c.bind("<ButtonRelease-1>", self.pointerup)
        self.canvas = c
        self.dy = 0
        self.items = []
        self.buttons = []
        for item in items:
            self.add(item)
        c.pack()
        self.initcanvas()
        self.updatecanvas()

    def add(self, element):
        self.items.append(element)
        self.buttons.append(
            self.ScrollListButton('item' + str(self.nextTag), y=0, value=element, fillcolor=self.fillcolor)
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
            self.h - self.items.__len__() * (self.item_height + self.item_padding) - self.padding[0] - self.padding[2],
            0)
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

    def remove_animation(self, button, stage=0):
        button.progress = 0
        self.remove(button=button)

    def initcanvas(self):

        if not self.figurecolor is None:
            round_rectangle(self.canvas, self.padding[3], self.padding[0], self.w - self.padding[1],
                            self.h - self.padding[2], radius=32, fill=self.figurecolor)
        y = self.dy + self.item_padding + self.padding[0]
        for button in self.buttons:
            self.draw_new(button, y)
            y += (self.item_height + self.item_padding)

        self.canvas.create_rectangle(self.padding[3], 0, self.w - self.padding[1], self.padding[0],
                                     outline=self.backgroundcolor,
                                     fill=self.backgroundcolor, tag='frame')
        self.canvas.create_rectangle(0, self.h - self.padding[2], self.w, self.h, outline=self.backgroundcolor,
                                     fill=self.backgroundcolor, tag='frame')

    def updatecanvas(self):
        y = self.dy + self.item_padding + self.padding[0]
        for button in self.buttons:
            if not button.needsupdate:
                if y > self.h and button.y > y and button.old_y > y:
                    continue
                if y != button.y:
                    self.canvas.move(button.tag, 0, y - button.y)
                    progress = self.canvas.find_withtag(button.tag + 'progress')
                    self.canvas.move(progress, 0, y - button.y)
                    text = self.canvas.find_withtag(button.tag + 'text')
                    self.canvas.move(text, 0, y - button.y)
                    button.set_y(y)
            else:
                self.canvas.delete(button.tag)
                self.canvas.delete(button.tag + 'text')
                self.canvas.delete(button.tag + 'progress')
                self.draw_new(button, y)

                # for particle in self.buttons[i]['particles']:
                #     self.canvas.create_rectangle(particle[0], particle[1], particle[2], particle[3], fill=self.backgroundcolor, outline=self.backgroundcolor)
            y += (self.item_height + self.item_padding)
        self.canvas.tag_raise('frame')
        self.update()

    def draw_new(self, button, y):
        print('new!')
        x0 = self.padding[3] + (self.w - self.padding[1] - self.padding[3] - self.item_width) / 2
        x1 = x0 + self.item_width
        if self.fillcolor is not None:
            round_rectangle(self.canvas, x0, y, x1, y + self.item_height,
                            radius=self.borderraadius, outline=button.fillcolor,
                            fill=button.fillcolor, tag=button.tag)
        if button.progress > 0.02:
            round_rectangle(self.canvas, x0 + self.progress_offset, y,
                            (self.item_width - self.progress_offset) * button.progress + x0 + self.progress_offset,
                            y + self.item_height,
                            radius=self.borderraadius, outline=self.loadcolor, fill=self.loadcolor,
                            tag=button.tag + 'progress')
        elif button.progress > 0:
            self.canvas.create_rectangle(x0 + self.progress_offset, y, (
                        self.item_width - self.progress_offset) * button.progress + x0 + self.progress_offset,
                                         y + self.item_height, outline=self.loadcolor, fill=self.loadcolor,
                                         tag=button.tag + 'progress')
        self.canvas.create_text((x1 + x0) / 2, y + self.item_height / 2, text=str(button.text),
                                fill=self.textcolor,
                                font=(button.font, button.fontsize),
                                tag=button.tag + 'text')
        button.set_y(y)
        button.needsupdate = False

    def sort(self, key=lambda item: item.progress, reverse=True, update=True):
        self.buttons = sorted(self.buttons, key=key, reverse=reverse)
        self.dy = 0
        if update:
            self.updatecanvas()

    def move(self, name, pos=None, up=False, down=False):
        for i in range(self.buttons.__len__()):
            if self.buttons[i].value == name:
                item = self.buttons[i]
                if pos is not None:
                    del self.buttons[i]
                    self.buttons.insert(pos, item)
                    return
                if up:
                    self.buttons.remove(item)
                    self.buttons.insert(i - 1, item)
                    return
                if down:
                    self.buttons.remove(item)
                    if self.buttons.__len__() > i + 1:
                        self.buttons.insert(i + 1, item)
                    else:
                        self.buttons.append(item)
                    return

    def pointerup(self, e):
        if ((e.x - self.pointerx) == 0 and (
                e.y - self.pointery) == 0 and e.y > self.padding[0] and e.y < self.w - self.padding[3]):
            for i in range(self.buttons.__len__()):
                if (e.y >= self.buttons[i].y and e.y <= self.buttons[i].y + self.item_height):
                    return

        if self.dy == self.padding[0] + self.item_padding:
            self.dy = 0
            self.updatecanvas()
        elif self.dy == self.visibleheight - self.padding[2]:
            self.dy = self.visibleheight
            self.updatecanvas()

        # self.lasty = 0
        # self.pointerx = 0
        # self.pointery = 0
        # self.updatecanvas()

    def pointerdown(self, e):
        self.pointerx = e.x
        self.pointery = e.y
        self.lasty = e.y

    def moved(self, d):

        ndy = d.y - self.lasty if d.delta == 0 else self.item_height * 0.9 if d.delta > 0 else -self.item_height * 0.9
        self.dy = self.dy + ndy
        # print(ndy, '  ', self.dy + ndy, '  ',
        #       min(self.padding / 2, self.dy + ndy) if ndy > 0 else max(self.dy + ndy, self.visibleheight), '  ',
        #       self.buttons[0].y, '   ', self.visibleheight)
        self.dy = min(self.padding[2] + self.item_padding, self.dy + ndy) if ndy > 0 else max(self.dy + ndy,
                                                                                              self.visibleheight -
                                                                                              self.padding[0])

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
        def __init__(self, tag, y, value=None, text=None, font='Colibri', fontsize=25, progress=0, fillcolor='#ffffff'):
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
        c = tk.Canvas(self, width=w, height=h, bg=backgroundcolor)
        c.bind("<Button-1>", self.clicked)
        c.pack()
        self.canvas = c
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
        round_rectangle(self.canvas, self.padding, self.padding, self.w - self.padding, self.h - self.padding,
                        radius=self.borderradius, outline=self.fillcolor, fill=self.fillcolor)
        # self.canvas.create_rectangle(0, 0, prorgess / 100 * self.w, self.h, outline=self.backgroundcolor, fill=self.backgroundcolor)
        self.canvas.create_text(self.w / 2, self.h / 2, text=self.text, fill=self.textcolor, font=self.font, tag='text')

    def drawProgress(self, prorgess):
        self.canvas.delete('text')
        self.canvas.delete('progress')
        if prorgess > 0:
            round_rectangle(self.canvas, self.padding, self.padding,
                            (self.w - self.padding * 2) * prorgess + self.padding,
                            self.h - self.padding,
                            radius=self.borderradius, outline=self.loadcolor, fill=self.loadcolor, tag='progress')
        if prorgess < 1:
            self.canvas.create_text(self.w / 2, self.h / 2, text=str(math.floor(prorgess * 100)) + '%',
                                    fill=self.textcolor,
                                    tag='text', font=self.font)
        else:
            self.canvas.create_text(self.w / 2, self.h / 2, text=str('done!'), fill=self.textcolor, tag='text',
                                    font=self.font)
            self.after(1000, self.updatecanvas)
        self.update()

    def watch_progress(self, progress):
        if progress.__len__() == 2:
            self.drawProgress(progress[0] / progress[1])
        if progress[0] / progress[1] < 1:
            self.after(500, lambda: self.watch_progress(progress))


class SimpleButton(tk.Frame):

    def __init__(self, parent, w=BUTTON_WIDTH + 2 * PADDING, h=BUTTON_HEIGHT + 2 * PADDING, backgroundcolor='#f1f0ec',
                 onclicked=None, text='+', textcolor='#ffffff',
                 fillcolor="#4978a6", loadcolor='#224b79', borderradius=18, padding=10, font=("Colibri", 25),
                 fixed=False):
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
        self.fixed = fixed
        self.state = False
        c = tk.Canvas(self, width=w, height=h, bg=backgroundcolor, bd=-2)
        c.bind("<Button-1>", self.clicked)
        c.pack()
        self.canvas = c
        self.updatecanvas(self.fillcolor)

    def clicked(self, e):
        if self.fixed:
            self.updatecanvas(self.loadcolor if not self.state else self.fillcolor)
            self.state = not self.state
            self.onclicked(self.state)
            self.updatecanvas(self.loadcolor if not self.state else self.fillcolor)
        else:
            self.updatecanvas(self.loadcolor)
            self.onclicked()
            self.updatecanvas(self.fillcolor)

    def updatecanvas(self, color=None):
        self.canvas.delete('all')
        color = self.fillcolor if color is None else color
        round_rectangle(self.canvas, self.padding, self.padding, self.w - self.padding, self.h - self.padding,
                        radius=self.borderradius, outline=color, fill=color)
        self.canvas.create_text(self.w / 2, self.h / 2, text=self.text, fill=self.textcolor, font=self.font)


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


class RuMap(tk.Frame):

    def __init__(self, parent, coords = None, hower_callback = lambda n: () , w=360, h=245, scaleX = 2):
        tk.Frame.__init__(self, parent)
        self.scaleX = scaleX
        self.coords = coords
        self.hover_region_tag = ''
        self.hower_callback = hower_callback
        c = tk.Canvas(self, width=w, height=h, bd=-2)
        c.pack()
        c.bind("<Motion>", self.map_hover)
        c.bind("<Button-1>", self.map_clicked)
        self.canvas = c
        self.draw_map(c)

    def map_clicked(self, details):
        ids = self.canvas.find_overlapping(details.x, details.y, details.x, details.y)
        if ids.__len__() != 1:
            return
        tag = self.canvas.gettags(ids[0])[0]
        print(tag)
        from threading import Thread
        if tag == 'open_new':
            Thread(target=self.open_new, args=([]), daemon=True).start()

    def open_new(self):
        app = tk.Tk()
        w = 360 * 2
        h = 245 * 2
        app.geometry(str(w)+'x'+str(h))
        c = RuMap(app, coords=self.coords, w = w, h = h, scaleX=4)
        c.pack()
        app.mainloop()

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

    def update_colors(self, regions):
        self.minreg = 999999
        self.maxreg = -99

        for reg in regions:
            self.minreg = min(self.minreg, self.regions[reg])
            self.maxreg = max(self.maxreg, self.regions[reg])

        if regions.__len__() > 0:
            for reg in regions:
                self.scrollList.setProgress(name=reg.replace('RU-', ''), progress=self.regions[reg] / self.maxreg * 0.9,
                                            text=' ' + str(self.regions[reg]))
            self.scrollList.sort()
        coords = self.regions_coordinates
        for reg in coords:
            if reg['name'] in regions:
                try:
                    regcolor = self.color_gradient[round((regions[reg['name']] - self.minreg) / (self.maxreg - self.minreg) * (
                            self.color_gradient.__len__() - 1))]
                except Exception as e:
                    regcolor = '#DDDDDD'
                    print(self.minreg, ' ', self.maxreg, ' ', regions[reg['name']], ' ', round(
                        (regions[reg['name']] - self.minreg) / (self.maxreg - self.minreg) * (
                                self.color_gradient.__len__() - 1)))

            else:
                regcolor = '#DDDDDD'
            self.canvas.itemconfigure(reg['name'], fill=regcolor)

    def draw_map(self, c):
        c.delete('all')
        for reg in self.coords:
            for poly in reg['coordinates'][0]:
                poly_coords = []
                scaleY = self.scaleX * 5 / 3
                offX = -15
                offY = 85
                for point in poly:
                    poly_coords += [(offX + point[1]) * self.scaleX, (offY - point[0]) * scaleY]
                c.create_polygon(poly_coords, fill='black', outline='black', tag=reg['name'] + '_shadow')
                c.create_polygon(poly_coords, fill='grey', outline='black', tag=reg['name'])
        self.canvas.create_oval(300, 190, 350, 240, outline="gray",
                                fill="gray", width=2, tag='open_new')
