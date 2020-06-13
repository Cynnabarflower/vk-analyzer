from Gui.Page import *
import tkinter as tk
from tkinter import ttk
import Gui.Gui as Gui
from Gui.Widgets import *
import matplotlib

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
        if 'first_name' in data:
            items['name'] = ['first name']
            if 'last_name' in data:
                items['name'] += ['last_name']
            if 'nickname' in data:
                items['name'] += ['nickname']
        if 'bdate' in data:
            items['age'] = ['bday', 'age_years']
            data['age_years'] = data['bdate'].map(lambda a: self.calc_age(a))
        if 'time_online' in data:
            items['time'] = ['online hours', 'avg day online']
        if 'sex' in data:
            items['sex'] = ['sex']
        if 'education_status' in data:
            items['education_status'] = ['education status']
        if "university_name" in data:
            items['university_name'] = ['university name']
        if 'detected_region' in data:
            items['region'] = ['region']

        items['followers_count'] = ['followers']
        items['region'] = ['region']
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

        self.canvases = []
        self.buttons = []
        self.top_canvas_windows = []
        t = 0
        self.items = {}
        self.setup_items(self.data)
        self.top_canvas = tk.Canvas(self, width = 550, height = 114, bg=Gui.background_color, bd=-2)
        self.top_canvas.grid(column = 0, row = 0, columnspan = 5)

        graphs = ['Moustache', 'Cluster', 'Dispersion', 'Pie', 'Histogram']

        for graph in graphs:
            fig = self.get_plot(self.data.sample(min(50, self.data.__len__())),
                                graph)
            self.fig = None
            fig.savefig('figure1.png', bbox_inches='tight', facecolor='#91b0cf', pad_inches=0)
            matplotlib.pyplot.clf()
            matplotlib.pyplot.cla()
            c = SimpleButton(self, onclicked=lambda b: self.clicked(b), w=550 / 5, h=550 / 5, text=str(graph),
                             icon=tk.PhotoImage(file='figure1.png'), fillcolor='#91b0cf', padding = 5)
            self.canvases.append(c)
            self.buttons.append(c)
            self.top_canvas_windows.append([self.top_canvas.create_window(t * 550/5, 0, window=c, anchor = 'nw'), t * 550/5, 0])
            # c.grid(row=2, column=t, sticky='nw')
            t += 1
        t = 0
        textCanvas = tk.Canvas(self, width=550, height=37, bg=Gui.background_color, bd=-2)
        textCanvas.create_text(275, 4, text='Qualicative', font=("Colibri", 20), fill='#4978a6',
                                    anchor="n")
        textCanvas.grid(column=0, row=2)

        b = RadioButton(self, header_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                                fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                                                                textcolor='#4978a6'),
                            child_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                        fillcolor='#91b0cf', loadcolor='#4978a6'),
                            can_choose_multiple=True, onclicked=None)
        # b.set_header("Qualicative:")
        b.add_value('bday')
        b.add_value('sex')
        b.add_value('education_status')
        b.add_value('region')
        b.grid(row = 3, column = 0, columnspan = 5)
        self.textCanvas = tk.Canvas(self, width=550, height=37, bg=Gui.background_color, bd=-2)
        self.textCanvas.create_text(275, 4, text='Quantitive', font=("Colibri", 20), fill='#4978a6',
                                    anchor="n")
        self.textCanvas.grid(column=0, row=4)

        b = RadioButton(self, header_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                                fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                                                                textcolor='#4978a6'),
                            child_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                        fillcolor='#91b0cf', loadcolor='#4978a6'),
                            can_choose_multiple=True, onclicked=None)
        # b.set_header("Quantitive:")
        b.add_value('age')
        b.add_value('followers_count')
        b.grid(row=5, column=0, columnspan=2)
        return


        if self.navigationNote:
            self.navigationNote.grid_forget()
        if self.note:
            self.note.grid_forget()
        self.navigationNote = Note(self)
        self.note = Note(self)
        frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, relief='flat', bd=0, height=550)
        self.note.add(frame)
        frame.configure(background=Gui.background_color, bd=-2)

        self.items = {}
        self.setup_items(self.data)

        self.page1 = self._Page1(frame, self.items)
        frame = tk.Frame(self.navigationNote, borderwidth=0, highlightthickness=0)
        frame.configure(background=Gui.background_color, bd=-2)
        SimpleButton(parent=frame, text='Next',
                     onclicked=lambda: self.fields_selected() or self.note.select(1) or self.navigationNote.select(1),
                     w=550, h=57,
                     padding=5).grid(row=5, column=0,
                                     columnspan=1 if self.page1.buttons.__len__() < 5 else self.page1.buttons.__len__() - 3 if self.page1.buttons.__len__() < 7 else 4,
                                     sticky='s')
        self.navigationNote.add(frame)
        frame = tk.Frame(self.navigationNote, borderwidth=0, highlightthickness=0)
        frame.configure(background=Gui.background_color, bd=-2)
        self.navigationNote.add(frame)
        SimpleButton(parent=frame, text="Done!",
                     onclicked=lambda: self.show_plot() or self.note.select(
                         self.note.pages.__len__() - 1) or self.navigationNote.select(2),
                     w=290, h=57, padding=5).grid(row=5,
                                                  column=1,
                                                  pady=0,
                                                  columnspan=2)
        SimpleButton(parent=frame, text='<', onclicked=lambda:
        self.note.select(previous=True) or self.note.current_index == 0 and self.navigationNote.select(0),
                     w=130, h=57, padding=5).grid(
            row=5, column=0, columnspan=1, pady=0)
        SimpleButton(parent=frame, text='>', onclicked=lambda: self.note.select(
            next=True) or self.note.current_index == 0 and self.navigationNote.select(0), w=130,
                     h=57, padding=5).grid(row=5, column=3, columnspan=1, pady=0)

        frame = tk.Frame(self.navigationNote, borderwidth=0, highlightthickness=0)
        frame.configure(background=Gui.background_color, bd=-2)
        self.navigationNote.add(frame)
        SimpleButton(parent=frame, text="Back",
                     onclicked=lambda: self.note.select(
                         previous=True) or self.note.remove(
                         self.note.pages.__len__() - 1) or self.navigationNote.select(
                         1) or self.note.current_index == 0 and self.navigationNote.select(0), w=550, h=57,
                     padding=5).grid(row=5, column=0)

        self.note.select(0)
        self.navigationNote.select(0)
        self.rowconfigure(0, weight=1)
        self.note.grid(column=0, row=0, sticky='n')
        self.navigationNote.grid(column=0, row=1, sticky='s')
        # self.note.pack(expand=1, fill='both', padx=0, pady=0, side='top')
        # self.navigationNote.pack(expand=1, fill='both', padx=0, pady=0, side='bottom')

    def clicked(self, b):
        self.init_show_graph(b.text, b)

    def init_show_graph(self, name, b):
        self.fig = None
        users = self.controller.get_users()
        if users.__len__() > 3000:
            users = users.sample(3000)
        self.fig = self.get_plot(users, name, lat=5, long=8, show_axes=True)
        b.updatecanvas(b.fillcolor)
        b.update()
        if self.fig:
            graphs.show_graph(self.fig)
            matplotlib.pyplot.clf()
            matplotlib.pyplot.cla()

    def get_plot(self, data, graph_type, lat=1, long=1, show_axes=False):
        if (graph_type) == 'Moustache':
            fig = graphs.moustache(data, 'sex', 'age_years', lat=lat, long=long, show_axes=show_axes)
        elif graph_type == 'Cluster':
            fig = graphs.klaster(data, 'sex', 'first_name', 'age_years', lat=lat, long=long, show_axes=show_axes)
        elif graph_type == 'Pie':
            fig = graphs.sweetie_pie(data, 'sex', size=lat, show_labels=show_axes)
        elif graph_type == 'Dispersion':
            fig = graphs.dispersion_diagram(data, 'age_years', 'sex', 'id', wid=lat, long=long, show_axes=show_axes)
        elif graph_type == 'Histogram':
            fig = graphs.kat_hist(data, 'age_years', 'sex', wid=lat, long=long, show_axes=show_axes)

        # fig.savefig('figure1.png', bbox_inches='tight', facecolor='#91b0cf')
        # fig = Figure(figsize=(1, 1))
        # # a = fig.add_subplot(111)
        # fig = data.plot(kind='bar', figsize = (1,1), legend = False, use_index = False)
        # # fig.axes('off')
        # # a.scatter(v, x, color='red')
        # # a.plot(p, range(2 + max(x)), color='blue')
        # # a.axis('off')
        #
        # # a.invert_yaxis()
        # fig.subplots_adjust(wspace=0, hspace=0)
        # fig.set_facecolor('#91b0cf')
        # # a.set_title ("Estimation Grid", fontsize=16)
        # # a.set_ylabel("Y", fontsize=14)
        # # a.set_xlabel("X", fontsize=14)
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
            # Дальше в init_show_graph (ctrl+click)
            self.init_show_graph(b.text)
            b.updatecanvas(b.fillcolor)
            b.update()

        def init_show_graph(self, name):
            # Тут получаем всех пользователей (data frame) и берем только 3000. Я очень не хотел этого делать, но
            # похоже нет способа строить график в другом потоке, а значит пока он строится программа зависает. Так что 3000
            # Кстати из-за этого графики каждый раз немного разные
            self.fig = None
            users = self.controller.get_users()
            if users.__len__() > 3000:
                users = users.sample(3000)
            # Я не помню почему просто не написал self.figure = self.get_plot(...)
            # В общем надо перелать get_plot - добавить ввод массива имен полей
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
                fig = graphs.moustache(data, 'sex', 'age_years', lat=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Cluster':
                fig = graphs.klaster(data, 'sex', 'first_name', 'age_years', lat=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Pie':
                fig = graphs.sweetie_pie(data, 'sex', size=lat, show_labels=show_axes)
            elif graph_type == 'Dispersion':
                fig = graphs.dispersion_diagram(data, 'age_years', 'sex', 'id', wid=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Histogram':
                fig = graphs.kat_hist(data, 'age_years', 'sex', wid=lat, long=long, show_axes=show_axes)
            return fig
