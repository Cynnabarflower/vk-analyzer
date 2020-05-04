from Gui.Page import *
import tkinter as tk
from tkinter import ttk
import Gui.Gui as Gui
from Gui.Widgets import *
import moustache_graph as mg

fields = ['id', 'first_name', 'last_name', 'sex', 'nickname', 'bdate', 'city', 'occupation', 'university_name', 'faculty_name', 'graduation', 'education_status', 'detected_region']

class TablePage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        self.table = TableWidget(self, w = 550, h = 400, data = [], fields = fields)
        self.table.grid(column = 0, row = 0, sticky='nsew')
        self.update_users([])


    def update_users(self, data):
        self.table.forget()
        self.table = TableWidget(self, data = data, w = 550, h = 400, data_changed = lambda users: self.controller.update_users(users), fields =fields)
        self.table.grid(column = 0, row = 0, sticky='nsew')
        if data.__len__() > 0:
            mg.show_moustache(data, data['first_name'], data['id'])



    def resize(self, w, h, aw, ah):
        self.table.resize(w,h, aw, ah)

    def get_users(self):
        return self.table.data
