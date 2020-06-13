from Gui.Page import *
import tkinter as tk
from tkinter import ttk
import Gui.Gui as Gui
from Gui.Widgets import *
import matplotlib
import os

matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from threading import Thread
from datetime import date
import graphs
import datanaliser


class AnalyzerPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.buttons = []
        self.canvases = []
        self.top_canvas_windows = []
        self.data = None
        self.note = None
        self.scale = (1.0, 1.0)
        self.navigationNote = None
        self.page1 = self.page2 = self.page3 = None
        self.top_canvas = None
        self.init_pages()

    def setup_items(self, data):
        if data is None:
            return
        items = {}
        if 'bdate' in data:
            items['age'] = ['bdate', 'age']
            data['age'] = data['bdate'].map(lambda a: self.calc_age(a))
        if 'sex' in data:
            items['sex'] = ['sex']
        if 'education_status' in data:
            items['education'] = ['education']
        if "university" in data:
            items['university'] = ['university']
        if 'region' in data:
            items['region'] = ['region']
        if 'followers_count' in data:
            items['followers_count'] = ['followers_count']
        self.items = items

    def calc_age(self, bday):
        if not bday is np.nan:
            bday = bday.split('.')
            if len(bday) == 3:
                bday = [int(i) for i in bday]
                d = date(bday[2], bday[1], bday[0])
                today = date.today()
                age = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
                return age
            else:
                return -1
        else:
            return -1

    def display_graphs(self):

        for win in self.top_canvas_windows:
            self.top_canvas.delete(win[0])

        self.canvases = []
        self.buttons = []
        self.top_canvas_windows = []


        graphs = ['Moustache', 'Cluster', 'Dispersion', 'Pie', 'Histogram']
        graphs = []
        b = self.qualicative_radio.get_selected() + self.quantative_radio.get_selected()
        if not ((("age" in b or "followers_count" not in b) and ("age" not in b or "followers_count" in b)) or b.__len__() != 2):
            graphs.append('Moustache')
            graphs.append('Histogram')
        if not (b.__len__() != 3 or (("age" in b or "followers_count" not in b) and ("age" not in b or "followers_count" in b))):
            graphs.append('Cluster')
        if  b.__len__() == 3 and not ("age" not in b or "followers_count" not in b):
            graphs.append('Dispersion')
        if b.__len__() == 1 and self.quantative_radio.get_selected().__len__() == 0:
            graphs.append('Pie')

        t = 0
        for graph in graphs:
            if not os.path.exists(os.getcwd()+'\\\\'+graph+'.png'):
                fig = self.get_plot(self.data.sample(min(50, self.data.__len__())),
                                    graph, sf=[0, 0, 0, 0, 0])
                self.fig = None
                fig.savefig(graph+'.png', bbox_inches='tight', facecolor='#91b0cf', pad_inches=0)
                matplotlib.pyplot.clf()
                matplotlib.pyplot.cla()
            c = SimpleButton(self, onclicked=lambda b: self.clicked(b), w=550 / 5, h=550 / 5, text=str(graph),
                             icon=tk.PhotoImage(file=graph+'.png'), fillcolor='#91b0cf', padding=5)
            self.canvases.append(c)
            self.buttons.append(c)
            self.top_canvas_windows.append(
                [self.top_canvas.create_window(t * 550 / 5, 0, window=c, anchor='nw'), t * 550 / 5, 0])
            # c.grid(row=2, column=t, sticky='nw')
            t += 1

    def init_pages(self):
        if self.note:
            self.note.grid_forget()
        if self.data is None or self.data.__len__() == 0:
            self.textCanvas = tk.Canvas(self, width=550, height=57, bg=Gui.background_color, bd=-2)
            self.textCanvas.create_text(275, 7, text='No data to analyze', font=("Colibri", 20), fill='#4978a6',
                                        anchor="n")
            self.textCanvas.grid(column=0, row=0)
            return


        # self.note = Note(self)
        # self.note.grid(column=0, row=1, columnspan=5)
        # frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, relief='flat', bd=0, height=57)
        # self.note.add(frame)
        # frame.configure(background=Gui.background_color, bd=-2)

        self.items = {}
        self.setup_items(self.data)
        self.top_canvas = tk.Canvas(self, width = 550, height = 114, bg=Gui.background_color, bd=-2)
        self.top_canvas.grid(column = 0, row = 0, columnspan = 5)

        textCanvas = tk.Canvas(self, width=550, height=37, bg=Gui.background_color, bd=-2)
        textCanvas.create_text(275, 4, text='Qualicative', font=("Colibri", 20), fill='#4978a6',
                                    anchor="n")
        textCanvas.grid(column=0, row=2)

        self.qualicative_radio = b = RadioButton(self, header_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                                fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                                                                textcolor='#4978a6'),
                            child_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                        fillcolor='#91b0cf', loadcolor='#4978a6'),
                            can_choose_multiple=True, onclicked= lambda a: self.display_graphs())
        # b.set_header("Qualicative:")
        b.add_value('bdate')
        b.add_value('sex')
        b.add_value('education_status')
        if 'region' in self.items:
            b.add_value('region')
        b.grid(row = 3, column = 0, columnspan = 5)
        self.textCanvas = tk.Canvas(self, width=550, height=37, bg=Gui.background_color, bd=-2)
        self.textCanvas.create_text(275, 4, text='Quantitive', font=("Colibri", 20), fill='#4978a6',
                                    anchor="n")
        self.textCanvas.grid(column=0, row=4)

        self.quantative_radio = b = RadioButton(self, header_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                                fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                                                                textcolor='#4978a6'),
                            child_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                        fillcolor='#91b0cf', loadcolor='#4978a6'),
                            can_choose_multiple=True, onclicked = lambda a: self.display_graphs())
        # b.set_header("Quantitive:")
        if 'age' in self.items:
            b.add_value('age')
        if 'followers_count' in self.items:
            b.add_value('followers_count')
        b.grid(row=5, column=0, columnspan=2)
        self.display_graphs()


    # def available(self, flags):
    #     for i in range(flags.__len__()):
    #         if not flags[i]:
    #             self.buttons[i].clicked = None
    #             self.buttons[i].fillcolor = "#F0F0ED"
    #             self.buttons[i].set_text("-")
    #             self.buttons[i].updatecanvas()
    #         else:
    #             self.buttons[i].clicked = lambda b: self.clicked(b)
    #             self.buttons[i].fillcolor = "#91b0cf"
    #     if flags[0]:
    #         self.buttons[0].set_text("Moustache")
    #         self.buttons[4].set_text("Histogram")
    #     if flags[1]:
    #         self.buttons[1].set_text("Cluster")
    #     if flags[2]:
    #         self.buttons[2].set_text("Dispersion")
    #     if flags[3]:
    #         self.buttons[3].set_text("Pie")
    #     for i in range(flags.__len__()):
    #         self.buttons[i].updatecanvas()

    def clicked(self, b):
        self.init_show_graph(b.text, b)

    def init_show_graph(self, name, b):
        self.fig = None
        selectedfields = self.qualicative_radio.get_selected() + self.quantative_radio.get_selected()
        users = self.controller.get_users()
        if users.__len__() > 3000:
            users = users.sample(3000)
        self.fig = self.get_plot(users, name, selectedfields, lat=5, long=8, show_axes=True)
        b.updatecanvas(b.fillcolor)
        b.update()
        if self.fig:
            graphs.show_graph(self.fig)
            matplotlib.pyplot.clf()
            matplotlib.pyplot.cla()

    def get_plot(self, data, graph_type, sf=[], lat=1, long=1, show_axes=False):
        q = quant = quant1 = quant2 = qual = qual1 = qual2 = ''
        fig = None
        if len(sf) == 1:
            q = sf[0]
            print('pie: ', q)
            # build pie
            if q in data.columns:
                print("it's here, ", q)
            else:
                print(q, "does not exist")
            fig = graphs.sweetie_pie(data, q, size=lat, show_labels=show_axes)

        elif len(sf) == 2:
            for i in sf:
                if i == 'age' or i == 'followers_count':
                    quant = i
                else:
                    qual = i
            if graph_type == 'Moustache':
                fig = graphs.moustache(data, qual, quant, lat=lat, long=long, show_axes=show_axes)
                print('moustache: ', quant, ', ', qual)
            elif graph_type == 'Histogram':
                fig = graphs.kat_hist(data, qual, quant, lat=lat, long=long, show_axes=show_axes)
                print('Hist: ', quant, ', ', qual)
            # build moustache or kat_hist


        elif len(sf) == 3:
            if 'age' in sf and 'followers_count' in sf:
                for i in sf:
                    if i != 'age' and i != 'followers_count':
                        qual = i
                    else:
                        if quant1 == '':
                            quant1 = i
                        quant2 = i
                print('dispersion: ', qual, ', ', quant1, ', ', quant2)
                # build dispersion
                fig = graphs.dispersion_diagram(data, quant1, quant2, qual, lat=lat, long=long,
                                                show_axes=show_axes)

            elif ('age' in sf or 'followers_count' not in sf) or (
                    'age' not in sf or 'followers_count' in sf):
                for i in sf:
                    if i == 'age' or i == 'followers_count':
                        quant = i
                    else:
                        if qual1 == '':
                            qual1 = i
                        qual2 = i
                print('cluster: ', quant, ', ', qual1, ', ', qual2)
                # build cluster
                fig = graphs.klaster(data, qual1, qual2, quant, lat=lat, long=long,
                                     show_axes=show_axes)
        if len(sf) == 5:
            if graph_type == 'Moustache':
                fig = graphs.moustache(data, 'sex', 'age', lat=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Cluster':
                fig = graphs.klaster(data, 'sex', 'first_name', 'age', lat=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Pie':
                fig = graphs.sweetie_pie(data, 'sex', size=lat, show_labels=show_axes)
            elif graph_type == 'Dispersion':
                fig = graphs.dispersion_diagram(data, 'id', 'age', 'sex', wid=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Histogram':
                fig = graphs.kat_hist(data, 'sex', 'age', lat=lat, long=long, show_axes=show_axes)
        return fig

    def update_users(self, users):
        self.data = users
        if self.note:
            self.note.forget()
        if self.navigationNote:
            self.navigationNote.forget()
        self.init_pages()

    def fields_selected(self):
        selected = []
        while self.note.pages.__len__() > 1:
            self.note.pages[1].forget()
            self.note.remove(1)
        for button in self.page1.buttons:
            if button.state:
                selected.append((button.text, self.items[button.text]))
                if selected.__len__() == 4:
                    frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0)
                    self.note.add(frame)
                    frame.configure(background=Gui.background_color, bd=-2)
                    self.page2 = self._Page2(frame, items=selected)
                    selected = []
        if selected.__len__() > 0:
            frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, height=550)
            self.note.add(frame)
            frame.configure(background=Gui.background_color, bd=-2)
            self.page2 = self._Page2(frame, items=selected)
            selected = []
        return self.note.pages.__len__() < 2

    def resize(self, w, h, aw, ah):
        print('Analyzer resized')
        if self.top_canvas:
            self.top_canvas.configure(width=aw * 550, height=ah * 550 / 5)
            for win in self.top_canvas_windows:
                self.top_canvas.move(win[0], win[1] * (aw-self.scale[0]), 0)
            for b in self.buttons:
                b.resize(min(w, h), min(w, h), min(aw, ah), min(aw, ah))
        self.scale = (aw, ah)


        # for f in self.navigationNote.pages:
        #     if hasattr(f, 'resize'):
        #         f.resize(w, h, aw, ah)
        #     elif hasattr(f, 'children'):
        #         for ch in f.children.values():
        #             if hasattr(ch, 'resize'):
        #                 ch.resize(w, h, aw, ah)
        # self.navigationNote.resize(w, h, aw, ah, all=True)

    def show_plot(self):
        if self.controller.get_users() is not None:
            frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, height=550)
            self.note.add(frame)
            frame.configure(background=Gui.background_color, bd=-2)
            self.page3 = self._Page3(frame, self.controller, self.page2.get_chosen())
            self.plot()

    class _Page3:
        def __init__(self, frame, controller, items):
            self.controller = controller
            self.canvases = []
            self.frame = frame
            self.buttons = []
            self.items = items
            t = 0

            graphs = ['Moustache', 'Cluster', 'Dispersion', 'Pie', 'Histogram']
            graph_buttons = []

            # Тут создаются кнопки
            # Кстати ctrl+click по вызову функции - перейти к объявлению функции
            for graph in graphs:
                # Для каждого типа графика получим фигуру на основании 40 случайных элементов
                fig = self.get_plot(self.controller.get_users().sample(min(40, self.controller.get_users().__len__())),
                                    graph)
                self.fig = None
                # Сохраним эту фигуру как картинку
                fig.savefig('figure1.png', bbox_inches='tight', facecolor='#91b0cf')
                # Эти 2 строки мб можно убрать
                matplotlib.pyplot.clf()
                matplotlib.pyplot.cla()
                # Непосредственно создание кнопки
                # В кнопку в onclicked передали лямбда функцию - она выполнится при клике на кнопку
                # Там как раз и показ графика и выбор столбцов
                c = SimpleButton(self.frame, onclicked=lambda b: self.clicked(b), w=525 / 5, h=525 / 5, text=str(graph),
                                 icon=tk.PhotoImage(file='figure1.png'), fillcolor='#91b0cf')
                self.canvases.append(c)
                self.buttons.append(c)
                # разместим кнопку на лэйауте
                c.grid(row=0, column=t, sticky='nw')
                t += 1

            SimpleButton(parent=frame, w=210, h=57, padding=5, text='Statistical reports:',
                         fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                         textcolor='#4978a6').grid(row=1, column=0, sticky='sw', columnspan=2)
            SimpleButton(parent=frame, w=105, h=57, padding=5, text='Summary',
                         fillcolor='#91b0cf', loadcolor='#4978a6', onclicked=self.reports_clicked).grid(row=1, column=2,
                                                                                                        sticky='sw')
            SimpleButton(parent=frame, w=105, h=57, padding=5, text='Quality',
                         fillcolor='#91b0cf', loadcolor='#4978a6', onclicked=self.reports_clicked).grid(row=1, column=3,
                                                                                                        sticky='sw')
            SimpleButton(parent=frame, w=105, h=57, padding=5, text='Quantity',
                         fillcolor='#91b0cf', loadcolor='#4978a6', onclicked=self.reports_clicked).grid(row=1, column=4,
                                                                                                        sticky='sw')

            SimpleButton(parent=frame, w=105, h=57, padding=5,
                         fillcolor=Gui.background_color, loadcolor=Gui.background_color, text='').grid(row=2, column=4,
                                                                                                       sticky='sw')
            b = RadioButton(frame, header_template=SimpleButton(parent=frame, w=105, h=57, padding=5,
                                                                fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                                                                textcolor='#4978a6'),
                            child_template=SimpleButton(parent=frame, w=105, h=57, padding=5,
                                                        fillcolor='#91b0cf', loadcolor='#4978a6'),
                            can_choose_multiple=True, onclicked=None)
            b.set_header("Fields:")
            for value in items.values():
                b.add_value(value[0])
            b.grid(row=3, column=0, sticky='sw', columnspan=5, rowspan=2)

            self.agg_radio = RadioButton(frame, header_template=SimpleButton(parent=frame, w=105, h=57, padding=5,
                                                                             fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                                                                             textcolor='#4978a6'),
                                         child_template=SimpleButton(parent=frame, w=75, h=57, padding=5,
                                                                     fillcolor='#91b0cf', loadcolor='#4978a6'),
                                         can_choose_multiple=False)
            self.agg_radio.set_header("Aggregation:")
            aggs = ['count', 'sum', 'min', 'max', 'mean', 'median']
            for val in aggs:
                self.agg_radio.add_value(val)
            self.agg_radio.grid(row=2, column=0, sticky='sw', columnspan=5, rowspan=1)

        def reports_clicked(self, b):
            if b.text == 'Summary':
                pass
                # graphs.piv()
            elif b.text == 'Quality':
                graphs.stkol()
                pass
            elif b.text == 'Quantity':
                # graph.stkach()
                pass
            pass

        def available(self, flags):
            for i in range(flags.__len__()):
                if not flags[i]:
                    self.buttons[i].clicked = None
                    self.buttons[i].fillcolor = "#F0F0ED"
                    self.buttons[i].set_text("-")
                    self.buttons[i].updatecanvas()
                else:
                    self.buttons[i].clicked = lambda b: self.clicked(b)
                    self.buttons[i].fillcolor = "#91b0cf"
            if flags[0]:
                self.buttons[0].set_text("Бокса-Вискера")
            if flags[1]:
                self.buttons[1].set_text("Кластер")
            if flags[2]:
                self.buttons[2].set_text("Дисперсия")
            if flags[3]:
                self.buttons[3].set_text("Пирог")
            for i in range(flags.__len__()):
                self.buttons[i].updatecanvas()

        def clicked(self, b):
            self.init_show_graph(b.text)
            b.updatecanvas(b.fillcolor)
            b.update()

        def init_show_graph(self, name):
            self.fig = None
            users = self.controller.get_users()
            if users.__len__() > 3000:
                users = users.sample(3000)
            self.set_fig(self.get_plot(users, name, lat=5, long=8, show_axes=True))
            self.wait_plot()

        def set_fig(self, fig):
            self.fig = fig

        def wait_plot(self):
            if self.fig:
                graphs.show_graph(self.fig)
                matplotlib.pyplot.clf()
                matplotlib.pyplot.cla()
            else:
                self.controller.after(500, self.wait_plot)

        def get_plot(self, data, graph_type, lat=1, long=1, show_axes=False):
            fig = None
            if (graph_type) == 'Moustache':
                fig = graphs.moustache(data, 'followers_count', 'age', lat=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Cluster':
                fig = graphs.klaster(data, 'followers_count', 'first_name', 'age', lat=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Pie':
                fig = graphs.sweetie_pie(data, 'followers_count', size=lat, show_labels=show_axes)
            elif graph_type == 'Dispersion':
                fig = graphs.dispersion_diagram(data, 'age', 'followers_count', 'id', wid=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Histogram':
                fig = graphs.kat_hist(data, 'age', 'followers_count', wid=lat, long=long, show_axes=show_axes)
            return fig
