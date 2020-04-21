from Gui.Page import *
import tkinter as tk
from tkinter import ttk
import Gui.Gui as Gui
from Gui.Widgets import *


class AnalyzerPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)


        self.navigationNote = ttk.Notebook(self, padding=0)
        self.note = ttk.Notebook(self, padding=0)
        frame = tk.Frame(self.note, borderwidth = 0, highlightthickness = 0, relief='flat', bd=0)
        self.note.add(frame)
        frame.configure(background=Gui.background_color, bd=-2)
        self._Page1(frame)

        self.items = {'name': ['prop1', 'prop2', 'prop3'], 'age': ['prop1', 'prop2', 'prop3'],
                      'time': ['prop1', 'prop2', 'prop3'],
                      'online': ['prop1', 'prop2', 'prop3'], 'friends': ['prop1', 'prop2', 'prop3'],
                      'sex': ['prop1', 'prop2', 'prop3'],
                      'education': ['prop1', 'prop2', 'prop3']}
        i = 0
        while i < self.items.__len__():
            frame = tk.Frame(self.note, borderwidth = 0, highlightthickness = 0)
            self.note.add(frame)
            frame.configure(background=Gui.background_color, bd=-2)
            self._Page2(frame, items=list(self.items.items())[i * 4:min(i * 4 + 5, self.items.__len__())])
            i += 4

        self.note.select(0)
        frame = tk.Frame(self.navigationNote, borderwidth = 0, highlightthickness = 0)
        frame.configure(background=Gui.background_color, bd=-2)
        SimpleButton(parent=frame, text='Next', onclicked=lambda: self.note.select(1) or self.navigationNote.select(1),
                     w=550, h=57,
                     padding=5).grid(row=5, column=0, columnspan=4)
        self.navigationNote.add(frame)
        frame = tk.Frame(self.navigationNote, borderwidth=0, highlightthickness=0)
        frame.configure(background=Gui.background_color, bd=-2)
        self.navigationNote.add(frame)
        SimpleButton(parent=frame, text="Done!", onclicked=lambda: print('Done!'), w=260, h=57, padding=5).grid(row=5,
                                                                                                                column=1,
                                                                                                                pady=0,
                                                                                                                columnspan=2)
        SimpleButton(parent=frame, text='<', onclicked=lambda: self.note.select(
            self.note.index(self.note.select()) - 1 if self.note.index(self.note.select()) > 0 else self.note.children.__len__() - 1)
                     or self.note.index(self.note.select()) == 0 and self.navigationNote.select(0),
                     w=130, h=57, padding=5).grid(
            row=5, column=0, columnspan=1, pady=0)
        SimpleButton(parent=frame, text='>', onclicked=lambda: self.note.select(
            self.note.index(self.note.select()) + 1 if self.note.index(self.note.select()) + 1 < self.note.children.__len__() else 0)
                     or self.note.index(self.note.select()) == 0 and self.navigationNote.select(0),
                     w=130,
                     h=57, padding=5).grid(row=5, column=3, columnspan=1, pady=0)
        self.note.select(0)

        self.note.pack(expand=1, fill='both', padx=0, pady=0, side='top')
        self.navigationNote.pack(expand=1, fill='both', padx=0, pady=0, side='bottom')

    class _Page1:
        def __init__(self, frame):
            self.textCanvas = tk.Canvas(frame, width=550, height=45, bg=Gui.background_color, bd=-2)
            self.textCanvas.create_text(275, 7, text='Choose fields to analyze', font=("Colibri", 20), fill='#4978a6',
                                        anchor="n")
            self.textCanvas.grid(row=0, column=0, columnspan=4)
            self.buttons = []
            for i in range(16):
                b = SimpleButton(parent=frame, text='item ' + str(i), onclicked=lambda: print(i), w=130, h=57,
                                 padding=5, fixed=True, fillcolor='#91b0cf', loadcolor='#4978a6')
                self.buttons.append(b)
                b.grid(row=i // 4 + 1, column=i % 4)

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
            next = -1
            t = 0
            for item in items:
                if t == 4:
                    break
                SimpleButton(parent=frame, text=item[0],
                             onclicked=lambda: print(i), w=130, h=57, padding=5, fixed=True,
                             fillcolor='#4978a6', loadcolor='#4978a6').grid(row=t % 4 + 1, column=0)
                for i in range(item[1].__len__()):
                    b = SimpleButton(parent=frame, text=item[1][i], onclicked=lambda: print(i), w=130, h=57, padding=5,
                                     fixed=True, fillcolor='#91b0cf', loadcolor='#4978a6')
                    self.buttons.append(b)
                    b.grid(row=t % 4 + 1, column=i % 3 + 1)
                t += 1
