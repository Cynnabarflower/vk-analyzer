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


class AnalyzerPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.data = None
        self.note = None
        self.navigationNote = None
        self.page1 = self.page2 = self.page3 = None
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
            if 'age_years' not in data:
                data['age_years'] = data['bdate'].map(lambda a: self.calc_age(a))
        if 'time_online' in data:
            items['time'] = ['online hours', 'avg day online']
        if 'sex' in data:
            items['sex'] = ['sex']
        if 'education' in data:
            items['education'] = ['education']
        self.items = items

    def calc_age(self,  bday):
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
                                     columnspan= 1 if self.page1.buttons.__len__() < 5 else self.page1.buttons.__len__() - 3 if self.page1.buttons.__len__() < 7 else 4,
                                     sticky='s')
        self.navigationNote.add(frame)
        frame = tk.Frame(self.navigationNote, borderwidth=0, highlightthickness=0)
        frame.configure(background=Gui.background_color, bd=-2)
        self.navigationNote.add(frame)
        SimpleButton(parent=frame, text="Done!",
                     onclicked=lambda: self.show_plot() or self.note.select(next=True) or self.navigationNote.select(2),
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
                         previous=True) or self.note.remove(self.note.pages.__len__() - 1) or self.navigationNote.select(
                         1) or self.note.current_index == 0 and self.navigationNote.select(0), w=550, h=57,
                     padding=5).grid(row=5, column=0)

        self.note.select(0)
        self.navigationNote.select(0)
        self.rowconfigure(0, weight=1)
        self.note.grid(column = 0, row = 0, sticky = 'n')
        self.navigationNote.grid(column=0, row=1, sticky = 's')
        # self.note.pack(expand=1, fill='both', padx=0, pady=0, side='top')
        # self.navigationNote.pack(expand=1, fill='both', padx=0, pady=0, side='bottom')

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
            frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, height = 550)
            self.note.add(frame)
            frame.configure(background=Gui.background_color, bd=-2)
            self.page2 = self._Page2(frame, items=selected)
            selected = []
        return self.note.pages.__len__() < 2

    def resize(self, w, h, aw, ah):
        print('Analyzer resized')
        # self.note.resize(w, h, aw, ah, all=True)
        if self.page1:
            self.page1.resize(w,h,aw,ah)
        if self.page2:
            self.page2.resize(w, h, aw, ah)
        if self.page3:
            self.page3.resize(w,h,aw,ah)
        for f in self.navigationNote.pages:
            if hasattr(f, 'resize'):
                f.resize(w, h, aw, ah)
            elif hasattr(f, 'children'):
                for ch in f.children.values():
                    if hasattr(ch, 'resize'):
                        ch.resize(w, h, aw, ah)
        self.navigationNote.resize(w, h, aw, ah, all=True)

    def show_plot(self):
        if self.controller.get_users() is not None:
            frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, height=550)
            self.note.add(frame)
            frame.configure(background=Gui.background_color, bd=-2)
            self.page3 = self._Page3(frame, self.controller, self.page2.get_chosen())
            self.plot()

    def plot (self):
        print('')


    class _Page1:
        def __init__(self, frame, items):
            self.items = items
            self.textCanvas = tk.Canvas(frame, width=550, height=57, bg=Gui.background_color, bd=-2)
            self.textCanvas.create_text(275, 7, text='Choose fields to analyze', font=("Colibri", 20), fill='#4978a6',
                                        anchor="n")
            self.textCanvas.grid(row=0, column=0, columnspan=4)
            self.buttons = []
            i = 0
            for item in self.items:
                b = SimpleButton(parent=frame, text=item, onclicked=lambda: print(item), w=130, h=57,
                                 padding=5, fixed=True, fillcolor='#91b0cf', loadcolor='#4978a6')
                self.buttons.append(b)

                b.grid(row=i // 4 + 1, column=i % 4, sticky = 'nw')
                i += 1

            while i < 16:

                b = SimpleButton(parent=frame,
                             w=130, h=57, padding=5,
                             fillcolor=Gui.background_color, loadcolor=Gui.background_color)
                b.grid(row=i // 4 + 1,column=i % 4, sticky = 'nw')
                self.buttons.append(b)
                i += 1

        def resize(self, w, h, aw, ah):
            for b in self.buttons:
                if b:
                    b.resize(w,h, aw, ah)

    class _Page2:
        def __init__(self, frame, items):
            self.items = items
            self.textCanvas = tk.Canvas(frame, width=550, height=45, bg=Gui.background_color, bd=-2)
            self.textCanvas.create_text(275, 7, text='Choose analyse properities', font=("Colibri", 20), fill='#4978a6',
                                        anchor="n")
            self.textCanvas.grid(row=0, column=0, columnspan=4)
            self.buttons = []
            self.props = []
            i = 0
            t = 1

            for item in items:
                b = RadioButton(frame, header_template=SimpleButton(parent=frame, w=130, h=57, padding=5,
                             fillcolor='#4978a6', loadcolor='#4978a6'), child_template = SimpleButton(parent=frame, w=130, h=57, padding=5,
                             fillcolor='#91b0cf', loadcolor='#4978a6'), can_choose_multiple = False)
                b.set_header(item[0])
                for value in item[1]:
                    b.add_value(value)

                self.buttons.append(b)
                b.grid(row=t, column=0, sticky = 'nw')
                t += 1


            #     SimpleButton(parent=frame, text=item[0],
            #                  onclicked=lambda: print(i), w=130, h=57, padding=5, fixed=True,
            #                  fillcolor='#4978a6', loadcolor='#4978a6').grid(row=t % 4 + 1, column=0)
            #     for i in range(item[1].__len__()):
            #         b = SimpleButton(parent=frame, text=item[1][i], onclicked=lambda: print(i), w=130, h=57, padding=5,
            #                          fixed=True, fillcolor='#91b0cf', loadcolor='#4978a6')
            #         self.buttons.append(b)
            #         b.grid(row=t % 4 + 1, column=i % 3 + 1)
            #     t += 1
            while t < 4:
                b = SimpleButton(parent=frame,
                             w=130, h=57, padding=5,
                             fillcolor=Gui.background_color, loadcolor=Gui.background_color)
                self.buttons.append(b)
                b.grid(row=t + 1,
                      column=0)
                t += 1

        def get_chosen(self):
            chosen = {}
            for b in self.buttons:
                if isinstance(b, RadioButton):
                    chosen[b.header.text] = b.get_selected()
            return chosen

        def resize(self, w, h, aw, ah):
            for b in self.buttons:
                if b:
                    b.resize(w,h, aw, ah)

    class _Page3:
        def __init__(self, frame, controller, items):
            self.controller = controller
            self.canvases = []
            self.frame = frame
            self.buttons = []
            self.items = items
            t = 0

            graphs = ['Moustache', 'Cluster', 'Dispersion', 'Pie']
            # Тут создаются кнопки
            #Кстати ctrl+click по вызову функции - перейти к объявлению функции
            for graph in graphs:
                #Для каждого типа графика получим фигуру на основании 40 случайных элементов
                fig = self.get_plot(self.controller.get_users().sample(min(40, self.controller.get_users().__len__())), graph)
                self.fig = None
                #Сохраним эту фигуру как картинку
                fig.savefig('figure1.png', bbox_inches='tight', facecolor='#91b0cf')
                #Эти 2 строки мб можно убрать
                matplotlib.pyplot.clf()
                matplotlib.pyplot.cla()
                #Непосредственно создание кнопки
                #В кнопку в onclicked передали лямбда функцию - она выполнится при клике на кнопку
                #Там как раз и показ графика и выбор столбцов
                c = SimpleButton(self.frame, onclicked = lambda b: self.clicked(b), w  = 535/4, h=535/4, text = str(graph), icon = tk.PhotoImage(file='figure1.png'), fillcolor = '#91b0cf')
                self.canvases.append(c)
                self.buttons.append(c)
                #разместим кнопку на лэйауте
                c.grid(row=t // 4, column= t % 4, sticky = 'nw')
                t += 1

        def clicked(self, b):
            #Дальше в init_show_graph (ctrl+click)
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
            # self.tt = Thread(target= lambda : self.set_fig(self.get_plot(self.controller.get_users(), name, lat = 5, long= 8, show_axes=True)))
            # self.tt.start()
            # multiprocessing.Process(target=lambda : self.set_fig(self.get_plot(self.controller.get_users().head(30), lat = 5, long= 8, show_axes=True))).start()
            self.wait_plot()


        def set_fig(self, fig):
            self.fig = fig

        def wait_plot(self):
            #Эта функция была нужна т.к я надеялся строить в другом потоке и каждые пол секунды проверять построился ли график
            #Теперь она по сути не нужна и выполняет функцию просто прослойки
            if self.fig:
                graphs.show_graph(self.fig)
                matplotlib.pyplot.clf()
                matplotlib.pyplot.cla()
            else:
                self.controller.after(500, self.wait_plot)

        def get_plot(self, data, graph_type, lat = 1, long = 1, show_axes = False):
            #Вот эту функцию надо изменить.
            # Надо добавить аргумент - массив (список) имен полей
            # Чтобы напрмер было: graphs.moustache(data, fields[0], fields[1], lat=lat, long=long, show_axes = show_axes)
            #Это не всё. Еще надо чтобы при создании кнопки сохранялиь поля с которыми она будет вызывать график
            #Чтобы одна кнопка вызывала Pie про sex, другая - Pie про age и тд
            #Для этого в массив buttons куда добовляется конпка можно добавлять не кнопку, а tuple например (button, ["field1", "field2", ...)
            #Этот массив используется в функции resize надо там соответственно чтобы не сломалось, вроде больше ни где не используется.
            if (graph_type) == 'Moustache':
                fig = graphs.moustache(data, 'sex', 'age_years', lat=lat, long=long, show_axes = show_axes)
            elif graph_type == 'Cluster':
                fig = graphs.klaster(data, 'sex', 'first_name', 'age_years', lat=lat, long=long, show_axes=show_axes)
            elif graph_type == 'Pie':
                fig = graphs.sweetie_pie(data, 'sex', size = lat, show_labels=show_axes)
            elif graph_type == 'Dispersion':
                fig = graphs.dispersion_diagram(data, 'id', 'age_years', 'sex', lat=lat, long=long, show_axes=show_axes)
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

        def resize(self, w, h, aw, ah):
            for b in self.buttons:
                if b:
                    b.resize(w,h, aw, ah)

        # def get_clickable_canvas(self, w, h, onclicked):
        #     def clicked(e):
        #         if onclicked:
        #             onclicked()
        #
        #
            # fig.savefig('figure1.png', bbox_inches='tight', facecolor='#91b0cf')
            # canvas = FigureCanvasTkAgg(fig, master=self.frame)
            # c = canvas.get_tk_widget()
            # c.configure(height=h, width = w, bd = 2)
            # canvas.draw()
            # # canvas = tk.Canvas(self.frame, width=w, height=h, bg = 'blue')
            # c.bind('<Button-1>', clicked)
            # return c