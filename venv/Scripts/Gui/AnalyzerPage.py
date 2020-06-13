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
            items['age'] = ['age']
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


        graphs = ['Moustache', 'Cluster', 'Dispersion', 'Pie', 'Histogram', 'Summary', 'Quality', 'Quantity']
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
        if self.qualicative_radio.get_selected().__len__() == 2:
            graphs.append('Summary')
        if self.qualicative_radio.get_selected().__len__() == 1:
            graphs.append('Quality')
        graphs.append('Quantity')

        t = 0
        for graph in graphs:
            if not os.path.exists(os.getcwd()+'\\\\'+graph+'.png'):
                fig = self.get_plot(self.data.sample(min(50, self.data.__len__())),
                                    graph, sf=[0, 0, 0, 0, 0])
                self.fig = None
                if fig:
                    fig.savefig(graph+'.png', bbox_inches='tight', facecolor='#91b0cf', pad_inches=0)
                    matplotlib.pyplot.clf()
                    matplotlib.pyplot.cla()
            if graph in ['Summary', 'Quality', 'Quantity']:
                c = SimpleButton(self, onclicked=lambda b: self.show_report(b.text), w=550 / 5, h=550 / 5, text=str(graph),
                                 icon=tk.PhotoImage(file='report.png'), fillcolor='#91b0cf', padding=5)
            else:
                c = SimpleButton(self, onclicked=lambda b: self.init_show_graph(b.text, b), w=550 / 5, h=550 / 5, text=str(graph),
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
        self.fields_note = Note(self)
        self.fields_note.grid(column=0, row=1, columnspan=5, rowspan=5, sticky = 's')
        frame = tk.Frame(self.fields_note, borderwidth=0, highlightthickness=0, relief='flat', bd=0, bg = 'red')
        self.fields_note.add(frame)
        self.fields_note.select(0)
        textCanvas = tk.Canvas(frame, width=10, height=37, bg=Gui.background_color, bd=-2)
        textCanvas.grid(column=0, row=0)
        textCanvas = tk.Canvas(frame, width=550, height=37, bg=Gui.background_color, bd=-2)
        textCanvas.create_text(275, 4, text='Qualicative', font=("Colibri", 20), fill='#4978a6',
                                    anchor="n")
        textCanvas.grid(column=0, row=2)

        self.qualicative_radio = b = RadioButton(frame, header_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                                fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                                                                textcolor='#4978a6'),
                            child_template=SimpleButton(parent=self, w=110, h=57, padding=5,
                                                        fillcolor='#91b0cf', loadcolor='#4978a6'),
                            can_choose_multiple=True, onclicked= lambda a: self.display_graphs())
        # b.set_header("Qualicative:")
        b.add_value('sex')
        b.add_value('education_status')
        if 'region' in self.items:
            b.add_value('region')
        b.grid(row = 3, column = 0, columnspan = 5)
        self.textCanvas = tk.Canvas(frame, width=550, height=37, bg=Gui.background_color, bd=-2)
        self.textCanvas.create_text(275, 4, text='Quantitive', font=("Colibri", 20), fill='#4978a6',
                                    anchor="n")
        self.textCanvas.grid(column=0, row=4)

        self.quantative_radio = b = RadioButton(frame, header_template=SimpleButton(parent=self, w=110, h=57, padding=5,
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

        frame = tk.Frame(self.fields_note, borderwidth=0, highlightthickness=0, relief='flat', bd=0)
        self.fields_note.add(frame)
        t = tk.Canvas(frame, width=10, height=37 + 37, bg=Gui.background_color, bd=-2)
        t.grid(column=0, row=0)
        self.textCanvas = tk.Canvas(frame, width=550, height=37, bg=Gui.background_color, bd=-2)
        self.textCanvas.create_text(275, 4, text='Choose aggregation function', font=("Colibri", 20), fill='#4978a6',
                                    anchor="n")
        self.textCanvas.grid(column=0, row=1)
        self.agg_radio = RadioButton(frame, header_template=SimpleButton(parent=frame, w=105, h=57, padding=5,
                                                                         fillcolor='#F0F0ED', loadcolor='#F0F0ED',
                                                                         textcolor='#4978a6'),
                                     child_template=SimpleButton(parent=frame, w=75, h=57, padding=5,
                                                                 fillcolor='#91b0cf', loadcolor='#4978a6'),
                                     onclicked = lambda a: self.show_report("Summary"),
                                     can_choose_multiple=False)
        aggs = ['count', 'sum', 'min', 'max', 'mean', 'median']
        for agg in aggs:
            self.agg_radio.add_value(agg)
        self.agg_radio.grid(column=0, row=2)
        b = SimpleButton(parent=frame, w=550, h=57, text = 'Back', padding=5, onclicked = lambda: self.back_from_aggs(), fillcolor='#91b0cf', loadcolor='#4978a6')
        b.grid(column = 0, row = 3, sticky = 's', rowspan = 2)
        self.display_graphs()

    def back_from_aggs(self):
        self.agg_radio.reset()
        self.fields_note.select(0)

    def show_report(self, b):
        if b == 'Quantity':
            s = graphs.stkol(self.data)
            self.back_from_aggs()
        elif b == 'Quality':
            s = graphs.stkach(self.data, self.qualicative_radio.get_selected()[0])
            self.back_from_aggs()
        else:
            q = self.qualicative_radio.get_selected()
            agg = self.agg_radio.get_selected()
            if agg.__len__() == 0:
                self.fields_note.select(1)
                return
            s = graphs.piv(self.data, q[0], q[1], agg[0])
        with open('f.html', 'w') as file:
            file.write(s.to_html())
        os.system("start "+os.getcwd()+r"\\f.html")

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
                    if quant1 == '':
                        quant1 = i
                    quant2 = i
                else:
                    if qual1 == '':
                        qual1 = i
                    qual2 = i
            if graph_type == 'Moustache':
                fig = graphs.moustache(data, qual, quant, lat=lat, long=long, show_axes=show_axes)
                print('moustache: ', quant, ', ', qual)
            elif graph_type == 'Histogram':
                fig = graphs.kat_hist(data, qual, quant, lat=lat, long=long, show_axes=show_axes)
                print('Hist: ', quant, ', ', qual)
            elif graph_type == 'Colourful_caterpillar':
                fig = graphs.barh(data, qual1, qual2, lat=lat, long=long, show_axes=show_axes)
                print('barh: ', qual1, ', ', qual2)
            elif graph_type == 'Line_graph':
                fig = graphs.line(data, quant1, quant2, lat=lat, long=long, show_axes=show_axes)
                print('line: ', quant1, ', ', quant2)


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
