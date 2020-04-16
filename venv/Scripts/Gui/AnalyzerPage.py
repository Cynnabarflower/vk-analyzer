from Gui.Page import *
import tkinter as tk
from tkinter import ttk
import Gui.Gui as Gui
from Gui.Widgets import *

class AnalyzerPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.note = ttk.Notebook(self, padding=0)
        frame = tk.Frame(self.note)
        self.note.add(frame)
        frame.configure(background=Gui.background_color)
        self.frame1 = frame

        frame = tk.Frame(self.note)
        self.note.add(frame)
        frame.configure(background=Gui.background_color)
        self.frame2 = frame

        self.load_screen1(self.frame1)
        self.load_screen2(self.frame2, items=['name', 'age', 'time', 'online', 'friends', 'sex', 'education'])

        self.note.pack(expand=1, fill='both', padx=0, pady=0, side='bottom')
        self.note.select(0)


    def load_screen1(self, frame):
        self.textCanvas = tk.Canvas(frame, width = 550, height = 45, bg=Gui.background_color, bd=-2)
        self.textCanvas.create_text(275, 7, text='Choose fields to analyze',  font=("Colibri", 20), fill='#4978a6', anchor="n")
        self.textCanvas.grid(row = 0, column = 0, columnspan = 4)

        self.buttons = []
        for i in range(16):
            b = SimpleButton(parent=frame, text='item '+str(i), onclicked=lambda: print(i), w=130,h=57, padding = 5, fixed = True, fillcolor='#91b0cf', loadcolor='#4978a6')
            self.buttons.append(b)
            b.grid(row = i // 4 + 1, column = i % 4)

        self.nextButton = SimpleButton(parent=frame, text='Next', onclicked=lambda: self.note.select(1), w=550,h=57, padding = 5).grid(row=5, column=0, columnspan=4)

    def load_screen2(self, frame, items):
        self.textCanvas = tk.Canvas(frame, width = 550, height = 45, bg=Gui.background_color, bd=-2)
        self.textCanvas.create_text(275, 7, text='Choose analyse properities',  font=("Colibri", 20), fill='#4978a6', anchor="n")
        self.textCanvas.grid(row = 0, column = 0, columnspan = 4)

        self.props = []
        i = 0
        next = -1
        t = 0
        for item in items:
            if t == 4:
                newframe = tk.Frame(self.note)
                self.note.add(newframe)
                next = self.note.children.__len__()
                newframe.configure(background=Gui.background_color)
                self.load_screen2(newframe, items = items[i:])
                break
            for i in range(4):
                b = SimpleButton(parent=frame, text= item if i % 4 == 0 else 'prop '+ str(i % 4), onclicked=lambda: print(i), w=130,h=57, padding = 5, fixed = True, fillcolor='#91b0cf' if i % 4 else '#4978a6', loadcolor='#4978a6')
                self.buttons.append(b)
                b.grid(row = t // 4 + 1, column = i % 4)
            t += 1

        doneButton = SimpleButton(parent=frame, text="Done!",
                                       onclicked=lambda: print('Done!'), w=260, h=57, padding=5).grid(row=5, column=1,
                                                                                                      columnspan=2)
        if self.note.children.__len__() > 2:
            prev = self.note.children.__len__() - 1 - (1 if next > 0 else 0)
            previousScreenButton = SimpleButton(parent=frame, text='<', onclicked=lambda:  self.note.select(prev), w=130,h=57, padding = 5).grid(row=5, column=0, columnspan=1)
        if next > 0:
            nextScreenButton = SimpleButton(parent=frame, text='>', onclicked=lambda: self.note.select(next), w=130,h=57, padding = 5).grid(row=5, column=3, columnspan=1)

