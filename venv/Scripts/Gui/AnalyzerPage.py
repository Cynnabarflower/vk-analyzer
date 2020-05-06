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


class AnalyzerPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_pages()

    def setup_items(self, items, data):
        self.items = items
        return
        if not data:
            return
        if 'first_name' in data:
            items['name'] += ['first name', 'normalized name']
        if 'last_name' in data:
            items['name'] += ['last_name']
        if 'bday' in data:
            items['age'] += ['bday', 'age']
        if 'time_online' in data:
            items['time'] += ['online hours', 'avg day online']


    def init_pages(self):
        self.navigationNote = Note(self)
        self.note = Note(self)
        frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, relief='flat', bd=0, height=550)
        self.data = None
        self.note.add(frame)
        frame.configure(background=Gui.background_color, bd=-2)

        self.possible_items = {'name': ['first_name', 'last_name', 'normalized_name'],
                      'age': ['prop1', 'prop2', 'prop3'],
                      'time': ['prop1', 'prop2', 'prop3'],
                      'online': ['prop1', 'prop2', 'prop3'],
                      'friends': ['prop1', 'prop2', 'prop3'],
                      'sex': ['prop1', 'prop2', 'prop3'],
                      'education': ['prop1', 'prop2', 'prop3']}

        self.items = {}
        self.setup_items(self.possible_items, self.data)

        self.page1 = self._Page1(frame, self.items)

        frame = tk.Frame(self.navigationNote, borderwidth=0, highlightthickness=0)
        frame.configure(background=Gui.background_color, bd=-2)
        SimpleButton(parent=frame, text='Next',
                     onclicked=lambda: self.fields_selected() or self.note.select(1) or self.navigationNote.select(1),
                     w=550, h=57,
                     padding=5).grid(row=5, column=0, columnspan=4, sticky='s')
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
                     onclicked=lambda: self.note.remove(self.note.pages.__len__() - 1) or self.note.select(
                         previous=True) or self.navigationNote.select(
                         1) or self.note.current_index == 0 and self.navigationNote.select(0), w=550, h=57,
                     padding=5).grid(row=5, column=0)

        self.note.select(0)
        self.navigationNote.select(0)
        self.note.pack(expand=1, fill='both', padx=0, pady=0, side='top')
        self.navigationNote.pack(expand=1, fill='both', padx=0, pady=0, side='bottom')

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
                    self._Page2(frame, items=selected)
                    selected = []
        if selected.__len__() > 0:
            frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, height = 550)
            self.note.add(frame)
            frame.configure(background=Gui.background_color, bd=-2)
            self._Page2(frame, items=selected)
            selected = []
        return self.note.pages.__len__() < 2

    def resize(self, w, h, aw, ah):
        print('Analyzer resized')
        self.note.resize(w, h, aw, ah, all=True)
        self.navigationNote.resize(w, h, aw, ah, all=True)

    def show_plot(self):
        frame = tk.Frame(self.note, borderwidth=0, highlightthickness=0, height=550)
        self.note.add(frame)
        frame.configure(background=Gui.background_color, bd=-2)
        self._Page3(frame, self.controller)
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
                b.grid(row=i // 4 + 1, column=i % 4)
                i += 1
            while i // 4 + 1 < 4:
                SimpleButton(parent=frame,
                             w=130, h=57, padding=5,
                             fillcolor=Gui.background_color, loadcolor=Gui.background_color).grid(row=i % 4 + 1,
                                                                                                  column=0)
                i += 4

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
            t = 0

            for item in items:
                b = RadioButton(frame, header_template =  SimpleButton(parent=frame, w=130, h=57, padding=5,
                             fillcolor='#4978a6', loadcolor='#4978a6'), child_template = SimpleButton(parent=frame, w=130, h=57, padding=5,
                             fillcolor='#91b0cf', loadcolor='#4978a6'), can_choose_multiple = False)
                b.set_header(item[0])
                for value in item[1]:
                    b.add_value(value)
                b.grid(row=t, column=0)
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
                SimpleButton(parent=frame,
                             w=130, h=57, padding=5,
                             fillcolor=Gui.background_color, loadcolor=Gui.background_color).grid(row=t % 4 + 1,
                                                                                                  column=0)
                t += 1

    class _Page3:
        def __init__(self, frame, controller):
            self.controller = controller
            self.canvases = []
            self.frame = frame
            t = 0
            graphs = [1,2,3,4,5,6,7,8]

            for graph in graphs:
                # self.get_clickable_canvas(535/4, 535/4, lambda: None)
                fig = self.get_plot(self.controller.get_users().head(40))
                fig.savefig('figure1.png', bbox_inches='tight', facecolor='#91b0cf')
                c = SimpleButton(self.frame, onclicked = lambda b: self.show_graph(b.text), w  = 535/4, h=535/4, text = str(graph), icon = tk.PhotoImage(file='figure1.png'), fillcolor = '#91b0cf')
                self.canvases.append(c)
                c.grid(row=t // 4, column= t % 4)
                t += 1

        def show_graph(self, name):
            print('')


        def get_plot(self, data):
            fig = Figure(figsize=(1, 1))
            # a = fig.add_subplot(111)
            fig = data.plot(kind='bar', figsize = (1,1), legend = False, use_index = False)
            fig.axes('off')
            # a.scatter(v, x, color='red')
            # a.plot(p, range(2 + max(x)), color='blue')
            # a.axis('off')

            # a.invert_yaxis()
            fig.subplots_adjust(wspace=0, hspace=0)
            fig.set_facecolor('#91b0cf')
            # a.set_title ("Estimation Grid", fontsize=16)
            # a.set_ylabel("Y", fontsize=14)
            # a.set_xlabel("X", fontsize=14)
            return fig

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