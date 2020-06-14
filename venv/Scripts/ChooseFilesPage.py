from Widgets import *
from Page import *
import Gui as Gui
import tkinter as tk
from tkinter import ttk
import json
from multiprocessing import Queue
from threading import Thread
import vk_caller as vk_caller
from PIL import Image, ImageTk
import requests
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
import traceback
import normalization


class ChooseFilesPage(Page):
    SCROLL_ITEM_HEIGHT = 50
    SCROLL_ITEM_WIDTH = 245
    SCROLL_ITEM_PADDING_X = 10
    SCROLL_ITEM_PADDING_Y = 10
    SCROLL_PADDING = 20
    SCROLL_WIDTH = SCROLL_ITEM_WIDTH + 2 * SCROLL_ITEM_PADDING_X
    SCROLL_HEIGHT = (SCROLL_ITEM_HEIGHT + SCROLL_ITEM_PADDING_Y) * 4
    WINDOW_WIDTH = 530
    WINDOW_HEIGHT = 360

    def __init__(self, parent, controller):
        """
        Initializing darframe, main fields and interface
        :param parent:
        :type parent:
        :param controller:
        :type controller:
        """
        super().__init__(parent, controller)
        self.filesToRead = []
        dtypes = np.dtype([
            ('id', int), ('first_name', str), ('last_name', str), ('sex', str), ('followers_count', int),
            ('bdate', str), ('city', int), ('occupation', str), ('university_name', str), ('graduation', int),
            ('education_status', str)
        ])
        self.users = pd.DataFrame(np.empty(0, dtypes))
        self.messages = pd.DataFrame()
        self.image = None
        self.loadedfiles = 0
        self.scrollList = ScrollList(self, onclicked=lambda e: self.scrollList.updatecanvas(),
                                     item_height=self.SCROLL_ITEM_HEIGHT,
                                     item_padding=self.SCROLL_ITEM_PADDING_Y, padding=(self.SCROLL_PADDING),
                                     w=self.SCROLL_WIDTH, h=self.SCROLL_HEIGHT)
        self.scrollList.grid(row=0, column=0)
        self.add_button = SimpleButton(self, onclicked=self.addFile, text='+')
        self.add_button.grid(row=1, column=0)
        self.rotatingcard = RotatingCard(self, view=self.rotating_view, init=self.init_rotating,
                                         clicked=self.rotating_clicked)
        self.rotatingcard.rotate(0)
        self.rotatingcard.grid(row=0, column=1)
        self.profile_image = None
        self.last_scale = (1, 1)
        self.profilePage = False
        self.conversations = []
        w = 265
        h = BUTTON_HEIGHT + 2 * PADDING
        self.filescanvas = canvas = tk.Canvas(self, width=w, height=h, bg='#F0F0ED')
        canvas.grid(row=1, column=1)
        self.filescountertext = canvas.create_text(w / 2, h / 2,
                                                   text='', font=('Colibri', 22), fill='#91b0cf')
        self.filescanvas.itemconfig(self.filescountertext, text=(
                str(self.loadedfiles) + " fies loaded"))

        self.update()

    def enter(self, w):
        """
        Changes focus on current InputField
        :param w:
        :type w:
        """
        c = tk.Canvas(self)
        c.focus_set()

    def init_rotating(self, canvas, w, h, padding, scale):
        """
        Initialize rotating card interface
        Not called directly, but set in RotatingCard instance
        :param canvas:
        :type canvas:
        :param w:
        :type w:
        :param h:
        :type h:
        :param padding:
        :type padding:
        :param scale:
        :type scale:
        """
        self.login_poly = -1

        self.inputPhone = InputField(self, canvas, padding + w / 11, padding + h / 4,
                                     w * 0.8 - padding * 2, h / 6, text='', bg='#ffffff', maxlen=12,
                                     empty_text='Phone:', on_enter=self.enter)

        self.inputPass = InputField(self, canvas, padding + w / 11, padding + h * 5 / 12 + 10,
                                    w * 0.8 - padding * 2, h / 6, text='', bg='#ffffff', is_password=True,
                                    empty_text='Password:      ', on_enter=self.enter)

        self.userscountertext = canvas.create_text(w / 2, padding + (h - 2 * padding) * 85 / 100,
                                                   text='12345678',
                                                   font=('Colibri', 26), fill='#ffffff')

        self.image_coords = getPolygons(
            'L 40.0 0.0 L 34.64132499254654 19.9994650618653 L 20.00106986196146 34.640398444257784 L 0.0018530717951983104 39.99999995707656 L -19.997860218846846 34.64225146648905 L -34.63947182162479 20.002674619131874 L -39.999999828306244 0.00370614358641961 L -34.64317786608332 -19.996255332909577 L -20.004279333373137 -34.63854512464951 L -0.00555921536969577 -39.999999613689056 L 19.994650404056877 -34.64410419132739 L 34.63761835333398 -20.005884004681747',
            1, w / 2, h * 0.22) \
                            + getPolygons(
            'M187.442 21.314 C 180.780 21.624,175.823 22.012,170.458 22.643 C 168.590 22.863,165.719 23.191,164.078 23.372 C 162.438 23.553,160.075 23.878,158.829 24.094 C 157.582 24.310,155.235 24.679,153.613 24.912 C 151.991 25.146,149.722 25.557,148.569 25.825 C 147.417 26.093,145.780 26.421,144.931 26.555 C 142.401 26.954,130.827 29.603,126.300 30.820 C 121.809 32.026,117.148 33.353,114.874 34.073 C 109.119 35.894,105.487 37.106,103.139 37.990 C 101.724 38.523,99.501 39.352,98.199 39.833 C 93.203 41.679,88.085 43.783,82.038 46.476 C 80.906 46.981,79.375 47.648,78.636 47.958 C 75.890 49.113,59.117 57.817,56.654 59.365 C 56.235 59.628,54.457 60.680,52.702 61.703 C 48.360 64.232,38.447 70.791,35.924 72.804 C 26.789 80.089,20.000 91.637,17.714 103.781 C 16.679 109.277,16.682 109.100,16.679 158.878 L 16.675 205.867 202.573 205.867 L 388.471 205.867 388.468 158.981 C 388.465 108.515,388.480 109.253,387.333 103.531 C 384.517 89.478,377.292 78.420,365.414 69.988 C 350.708 59.547,328.654 48.132,307.566 40.046 C 301.685 37.791,298.563 36.669,295.522 35.720 C 293.824 35.189,291.462 34.447,290.273 34.070 C 284.901 32.368,271.725 28.893,267.422 28.043 C 263.700 27.308,260.015 26.554,257.042 25.920 C 255.466 25.583,252.919 25.125,251.381 24.901 C 249.843 24.676,247.195 24.264,245.497 23.985 C 243.798 23.706,241.390 23.380,240.144 23.261 C 238.899 23.142,236.814 22.913,235.512 22.751 C 223.436 21.253,202.317 20.621,187.442 21.314',
            0.4, w / 2, h * 0.4)

        self.login_button_text = canvas.create_text(padding + w / 11 * scale[0] + (w * 0.4 - padding) * scale[0],
                                                    (h * 7 / 12 + 30) * scale[1] + h / 12 * scale[1], text='Logout',
                                                    font=fit_text((w * 0.8 - padding) * scale[0] * 0.8,
                                                                  h / 6 * scale[1] * 0.8, 'Logout',
                                                                  ('Colibri', 24)), fill='#ffffff',
                                                    tag='login_button_text')
        self.login_progress_bar = ProgressBar(self, canvas,
                                              padding + w / 11 * scale[0] + (w * 0.4 - padding) * scale[0],
                                              (h * 7 / 12 + 30) * scale[1] + h / 12 * scale[1],
                                              h / 6 * self.scale[1] * 0.25, h / 6 * self.scale[1] * 0.4, '#91b0cf',
                                              '#224b79')

        print('')

    def rotating_view(self, canvas, w, h, padding, scale, a):
        """
        Should not be called directly
        Set in RotatingCard instance
        Called when the card in rotating
        :param canvas:
        :type canvas:
        :param w:
        :type w:
        :param h:
        :type h:
        :param padding:
        :type padding:
        :param scale:
        :type scale:
        :param a:
        :type a:
        """
        self.inputPhone.hide()
        self.inputPass.hide()
        canvas.delete(self.login_poly)
        canvas.delete('profile_image_frame')
        canvas.delete('profile_image')
        canvas.itemconfigure(self.login_button_text, state='hidden')
        self.login_progress_bar.set_visible(False)
        alpha = (a % 360) * math.pi / 180
        if a == 90:
            self.scrollList.reset()
            self.scrollList.choosable = True
            for conversation in self.conversations:
                self.scrollList.add(conversation[0])
        elif a == 270:
            self.scrollList.reset()
            self.scrollList.choosable = False

        if a < 90 or a > 270:
            self.login_progress_bar.set_visible(False)
            self.profilePage = False
            for poly in self.image_coords:
                points = poly.copy()
                for i in range(0, points.__len__(), 2):
                    points[i] = ((w / 2) * scale[0] + ((points[i] - (w / 2) * scale[0])) * math.cos(
                        alpha)) * scale[0]
                    points[i + 1] = points[i + 1] * scale[1]
                canvas.create_polygon(points, fill='#ffffff', tag='img', smooth=True)

            if (a % 180) < 10:
                canvas.itemconfigure(self.userscountertext, state='normal', text=str(self.users.__len__()))
                canvas.coords(self.userscountertext, w / 2 * scale[0],
                              padding + (h - 2 * padding) * 0.85 * scale[1])
                canvas.lift(self.userscountertext)
                if a == 0:
                    self.add_button.set_text('+')
                    self.add_button.updatecanvas()
            else:
                canvas.itemconfigure(self.userscountertext, state='hidden')

        else:
            if a == 180:
                self.add_button.set_text('Load conversations')
                self.add_button.updatecanvas()
            self.profilePage = True
            alpha = (alpha - math.pi) % 3.1415

            points = round_rectangle_points(padding + w / 11 * scale[0],
                                            (h * 7 / 12 + 30) * scale[1],
                                            (w / 11 + w * 0.8 - padding) * scale[0],
                                            (h * 9 / 12 + 30) * scale[1],
                                            )
            rotate_polygon(points, (w / 2) * scale[0], 0, oy=alpha)
            self.login_poly = canvas.create_polygon(points, fill='#224b79', tag='login_poly', smooth=True)

            if self.profile_image:
                if (a % 180) < 10:
                    side = math.floor((h / 6 * 2.9) * min(scale[0], scale[1]))
                    self.profile_image_scaled = ImageTk.PhotoImage(
                        self.profile_image.resize((side, side), Image.ANTIALIAS))
                    img2 = canvas.create_image(w / 2 * scale[0], h * 6 / 16 * scale[1], image=self.profile_image_scaled,
                                               tag='profile_image')
                    polys = round_frame_points(w / 2 * scale[0], h * 6 / 16 * scale[1],
                                               self.profile_image_scaled.width() + 2,
                                               self.profile_image_scaled.height() + 2, radius=12 * min(scale))
                    for points in polys:
                        rotate_polygon(points, (w / 2) * scale[0], 0, oy=alpha)
                        canvas.create_polygon(points, fill='#91b0cf', tag='profile_image_frame', smooth=True)

                    canvas.itemconfigure(self.login_button_text, state='normal', text='Logout',
                                         font=fit_text((w * 0.8 - padding) * scale[0] * 0.8, h / 6 * scale[1] * 0.8,
                                                       'Logout',
                                                       ('Colibri', 24)))
                    c = canvas.coords(self.login_button_text)
                    canvas.move(self.login_button_text,
                                padding + w / 11 * scale[0] + (w * 0.4 - padding) * scale[0] - c[0],
                                (h * 7 / 12 + 30) * scale[1] + h / 12 * scale[1] - c[1])
                    canvas.lift(self.login_button_text)

            else:

                points = round_rectangle_points(self.inputPhone.x * scale[0],
                                                self.inputPhone.y * scale[1],
                                                (self.inputPhone.x + self.inputPhone.w) * scale[0],
                                                (self.inputPhone.y + self.inputPhone.h) * scale[1],
                                                )
                rotate_polygon(points, (w / 2) * scale[0], 0, oy=alpha)
                canvas.create_polygon(points, fill=self.inputPhone.bg, tag=self.inputPhone.id, smooth=True)
                # self.inputPhone.x = (padding + w / 11) * scale[0]

                points = round_rectangle_points(self.inputPass.x * scale[0],
                                                self.inputPass.y * scale[1],
                                                (self.inputPass.x + self.inputPass.w) * scale[0],
                                                (self.inputPass.y + self.inputPass.h) * scale[1],
                                                )
                rotate_polygon(points, (w / 2) * scale[0], 0, oy=alpha)
                canvas.create_polygon(points, fill=self.inputPass.bg, tag=self.inputPass.id, smooth=True)
                # self.inputPass.x = (padding + w / 11) * scale[0]

                if (a % 180) < 10:
                    c = canvas.coords(self.login_button_text)
                    canvas.move(self.login_button_text,
                                padding + w / 11 * scale[0] + (w * 0.4 - padding) * scale[0] - c[0],
                                (h * 7 / 12 + 30) * scale[1] + h / 12 * scale[1] - c[1])

                    self.inputPhone.init_canvas()
                    self.inputPass.init_canvas()
                    if not self.login_progress_bar.working:
                        canvas.itemconfigure(self.login_button_text, state='normal', text='Login',
                                             font=fit_text((w * 0.8 - padding) * scale[0] * 0.8, h / 6 * scale[1] * 0.8,
                                                           'Login',
                                                           ('Colibri', 24)))
                        canvas.lift(self.login_button_text)
                    else:
                        self.login_progress_bar.set_visible(True)
                        pb_x = padding + w / 11 * scale[0] + (w * 0.4 - padding) * scale[0]
                        pb_y = (h * 7 / 12 + 30) * scale[1] + h / 12 * scale[1]
                        if pb_x != self.login_progress_bar.x or pb_y != self.login_progress_bar.y:
                            self.login_progress_bar.move(pb_x, pb_y)

    def rotating_clicked(self, e, canvas, w, h, padding, scale, a):
        """
        Shoul not be called directly,
        but set in RotatingCard instance
        Called when rotating card is clicked, but not rotating button
        :param e:
        :type e:
        :param canvas:
        :type canvas:
        :param w:
        :type w:
        :param h:
        :type h:
        :param padding:
        :type padding:
        :param scale:
        :type scale:
        :param a:
        :type a:
        """
        if a > 3.1415 / 2 and a < 3.1415 * 1.5:
            if not max(self.inputPhone.clicked(e), self.inputPass.clicked(e)):
                if self.login_poly in canvas.find_overlapping(e.x, e.y, e.x, e.y):
                    if not self.login_progress_bar.working:
                        if self.profile_image is None:
                            canvas.itemconfigure(self.login_button_text, state='hidden')
                            self.login_progress_bar.set_visible(True)
                            self.login_progress_bar.working = True
                            self.login_progress_bar.drawprogress()
                            self.update()
                            thr = Thread(target=lambda: self.login(self.inputPhone.text, self.inputPass.text),
                                         daemon=True)
                            thr.start()
                            self.wait_login(thr)
                        else:
                            self.profile_image = None
                            self.profile_image_scaled = None
                            self.rotatingcard.rotate(180)
                        # self.login(self.inputPhone.text, self.inputPass.text)

    def wait_login(self, thr):
        """
        Waits for login to complete
        and after, updates interface
        :param thr:
        :type thr:
        """
        if self.profile_image:
            thr.join()
            self.login_progress_bar.working = False
            self.scrollList.reset()
            self.scrollList.choosable = True
            for conversation in self.conversations:
                self.scrollList.add(conversation[0])
            self.scrollList.updatecanvas()
            self.rotatingcard.rotate(180)
        else:
            self.after(300, lambda: self.wait_login(thr))

    def resize(self, w, h, aw, ah):
        """
        Called whenever the window is resized
        Resizes widgets
        :param w:
        :type w:
        :param h:
        :type h:
        :param aw:
        :type aw:
        :param ah:
        :type ah:
        """
        print('FilePage resized', w, h, aw, ah)
        self.add_button.resize(w, h, aw, ah)
        self.scrollList.resize(w, h, aw, ah)
        self.filescanvas.configure(width=aw * 265, height=ah * (BUTTON_HEIGHT + 2 * PADDING))
        current_scale = (aw / self.last_scale[0], ah / self.last_scale[1])
        self.filescanvas.scale('all', 0, 0, current_scale[0], current_scale[1])
        self.last_scale = (aw, ah)
        self.inputPhone.resize(w, h, aw, ah)
        self.inputPass.resize(w, h, aw, ah)
        self.rotatingcard.resize(w, h, aw, ah)

    def login(self, tel, pas):
        """
        Logs in with given tel and pass
        Loads data from profile
        :param tel:
        :type tel:
        :param pas:
        :type pas:
        """
        print('Logging in')
        self.admin_apis = vk_caller.VKFA(tel, pas)
        auth = self.admin_apis.auth()
        if auth:
            print('Login complete')
        resp = self.admin_apis.users.get(fields='photo_200')
        print('Photo loaded')
        print('Loading profile data...')
        self.getUserInfo(filename='User data')
        self.addFile(addedFiles=['User data'])
        print('Loading conversations...')
        conversations = self.admin_apis.messages.getConversations(count=12)
        for conversation in conversations['items']:
            if conversation['conversation']['peer']['type'] == 'user':
                time.sleep(0.4)
                user = self.admin_apis.users.get(user_id=str(conversation['conversation']['peer']['id']))
                if isinstance(user, Exception):
                    continue
                conversation_name = user[0]['first_name'] + ' ' + user[0]['last_name']
                self.conversations.append((conversation_name, conversation))
            else:
                if ('chat_settings' in conversation['conversation']):
                    conversation_name = conversation['conversation']['chat_settings']['title']
                    self.conversations.append((conversation_name, conversation))
        photo_url = resp[0]['photo_200']
        self.profile_image = Image.open(requests.get(photo_url, stream=True).raw)

    def getUserInfo(self, user_id='', filename='', user_fields=None):
        """
        Return dict with information about user. possible user_fields: nickname, screen_name, sex, bdate, city,
        country, timezone, photo, has_mobile, contacts, education, online, counters, relation, last_seen, activity,
        can_write_private_message, can_see_all_posts, can_post, universities, followers_count, counters, occupation
        :param user_id: :type user_id: :param filename: :type filename: :param user_fields: :type user_fields:
        :return: :rtype:
        """
        fields = [
            'nickname, screen_name, sex, bdate, city, country, timezone, photo, has_mobile, contacts, education, online, counters, relation, last_seen, activity, can_write_private_message, can_see_all_posts, can_post, universities, followers_count, counters, occupation']
        if not (user_fields is None):
            if isinstance(user_fields, str):
                fields = [user_fields]
            elif isinstance(user_fields, list):
                fields = user_fields
            else:
                print('Incorrect user fields, should be str')
                return
        user = self.admin_apis.users.get(user_id=user_id, fields=fields)
        attempt = 1

        while isinstance(user, Exception) and attempt < 10:
            if user.args[0]['error_code'] in vk_caller.VK_ERRORS:
                print(str(user.args[0]['error_msg']))
                return None
            print('Exception in getUserInfo sleeping..  ' + str(user.args[0]['error_msg']))
            time.sleep(2 * attempt)
            user = self.admin_apis.users.get(user_id=user_id, fields=fields)
            attempt = attempt + 1
        if attempt == 10:
            return None
        user = user[0]
        if filename:
            f = open(filename, "w", True, 'UTF-8')
            f.write('[[' + json.dumps(user) + ']]')
            f.close()
        return user

    def add_conversation(self):
        """
        Inits download for choosen conversations
        :return: 
        :rtype: 
        """
        self.login_progress_bar.set_visible(True)
        self.login_progress_bar.working = True
        self.login_progress_bar.drawprogress()
        self.login_progress_bar.canvas.itemconfigure(self.login_button_text, state='hidden')
        conversations_to_load = []
        for item in self.scrollList.buttons.copy():
            if item.isChosen:
                for conversation in self.conversations:
                    if conversation[0] == item.value:
                        self.scrollList.remove(button=item)
                        conversations_to_load.append(conversation[1])
        self.scrollList.updatecanvas()
        if conversations_to_load.__len__() > 0:
            q = Queue()
            Thread(target=lambda: self.loadConversations(conversations_to_load, q), daemon=True).start()
            self.wait_load_conversations(q)
        else:
            self.login_progress_bar.canvas.itemconfigure(self.login_button_text, state='normal')
            self.login_progress_bar.set_visible(False)
            self.login_progress_bar.working = False
            return

    def wait_load_conversations(self, q):
        """
        Waits for conversations to download
        and loads them into base
        :param q:
        :type q:
        """
        if not q.empty():
            rep = q.get()
            self.addFile(addedFiles=rep)
        else:
            self.after(200, lambda: self.wait_load_conversations(q))

    def addFile(self, _, addedFiles=None):
        """
        Inits load of given files
        If no files given - opens file choose dialog
        If choosing conversations - inits conversations load
        :param addedFiles:
        :type addedFiles:
        :return:
        :rtype:
        """
        if self.profilePage and addedFiles is None:
            self.add_conversation()
            return
        elif addedFiles is None:
            addedFiles = tk.filedialog.askopenfilenames(title="Select vka file",
                                                        filetypes=([("All", "*.*"), ("vka", "*.vka")]))
        for addedFile in addedFiles:
            if addedFile:
                self.filesToRead += [addedFile]
                self.scrollList.add(addedFile.split('/')[-1])
        self.filescanvas.itemconfig(self.filescountertext, text=(
                str(self.loadedfiles) + " of " + str(self.loadedfiles + self.filesToRead.__len__()) + " loaded..."))
        self.load_files_launch()

    def load_files_launch(self):
        """
        Inits files load
        Shows progress
        """
        q = Queue()
        Thread(target=self.load_files, args=[q], daemon=True).start()
        while True:
            rep = q.get()
            if rep == 'DONE':
                break
            print(str(rep))
            if rep.__len__() == 2:
                filename = rep[0]
                progress = rep[1]
                self.scrollList.setProgress(name=filename, progress=progress)
            else:
                self.loadedfiles = rep[0]
                self.controller.update_users(self.users)
                if self.messages is not None and not self.messages.empty:
                    self.messages['text'] = self.messages['text'].map(lambda a: self.normalize_text(a))
                self.controller.update_text(self.messages)
                self.filescanvas.itemconfig(self.filescountertext, text=(
                        str(self.loadedfiles) + " of " + str(self.filesToRead.__len__()) + " loaded..."))
                self.update()
        self.login_progress_bar.set_visible(False)
        self.login_progress_bar.working = False
        self.login_progress_bar.canvas.itemconfigure(self.login_button_text, state='hidden')

        self.loadedfiles = self.filesToRead.__len__()
        self.filesToRead = []
        self.filescanvas.itemconfig(self.filescountertext, text=(
                str(self.loadedfiles) + " files loaded"))
        q.close()

    def normalize_text(self, text):
        """
        Normalizes function
        Wrapper for normalization.text_normalise function
        :param text:
        :type text:
        :return:
        :rtype:
        """
        try:
            return normalization.text_normalize(a, ['а', 'и', ','])
        except Exception as e:
            return text

    def load_files(self, q):
        """
        Loads files one by one and puts progress into queue
        :param q: 
        :type q: 
        """
        progress = 0
        if self.filesToRead.__len__() > 0:
            for file in self.filesToRead:
                if file.endswith('vkmsg'):
                    self.load_messages_file(file, q)
                else:
                    self.load_file(file, q)
                progress += 1
                q.put([progress])
        q.put('DONE')

    def load_messages_file(self, file, q):
        """
        loads messages files and puts progress into queue
        :param file: 
        :type file: 
        :param q: 
        :type q: 
        """
        q.put([file, 0])
        f = open(file, 'r')
        filename = file.split('/')[-1]
        counter = 0
        js_packs = json.load(f)
        total = js_packs.__len__() + 1
        for js in js_packs:
            counter += 1
            pack = pd.DataFrame(js)[['from_id', 'text']]
            pack['text'] = pack['text'].map(lambda a: a + ' ')
            pack = pack.groupby(['from_id'], as_index=False).sum()
            self.messages = self.messages.append(pack).groupby(['from_id'], as_index=False).sum()
            q.put((filename, counter / total))

        self.messages = self.messages[self.messages['text'].str.strip().astype(bool)]
        q.put((filename, 1))
        self.after(100, lambda: self.scrollList.remove(name=filename) or self.scrollList.updatecanvas())

    def load_file(self, file, q):
        """
        loads file and adds it into database
        :param file: 
        :type file: 
        :param q: 
        :type q: 
        """
        q.put([file, 0])
        import time as t
        f = open(file, 'r')
        print(t.time())
        filename = file.split('/')[-1]
        counter = 0
        if file.endswith('csv'):
            try:
                self.users = self.users.append(pd.read_csv(file, encoding='utf-8', engine='python'))
                self.users.drop_duplicates(subset='id', inplace=True, keep='last')
            except:
                try:
                    self.users = self.users.append(pd.read_csv(file, encoding='ANSI', engine='python'))
                    self.users.drop_duplicates(subset='id', inplace=True, keep='last')
                except:
                    print("Error when reading file")

        else:
            js_packs = json.load(f)
            total = js_packs.__len__() + 1
            for js in js_packs:
                counter += 1
                users = pd.DataFrame(js)

                users['city'] = users['city'].map(lambda a: 0 if pd.isna(a) or not isinstance(a, dict) else a['id'])
                users['city'] = users['city'].astype('int32')
                users['occupation'] = users['occupation'].map(
                    lambda a: "" if pd.isna(a) or not isinstance(a, dict) or a['type'] != 'work' else a['name'])
                users['university_name'].fillna('', inplace=True)
                users['university_name'] = users['university_name'].astype(str)
                users['bdate'].fillna('', inplace=True)
                users['bdate'] = users['bdate'].astype(str)
                users['graduation'].fillna(-1, inplace=True)
                users['graduation'] = users['graduation'].astype(int)
                users['followers_count'].fillna(-1, inplace=True)
                users['followers_count'] = users['followers_count'].astype(int)
                users['education_status'].fillna('', inplace=True)
                users['education_status'] = users['education_status'].astype(str)
                users['id'] = users['id'].astype(int)
                users['sex'] = users['sex'].map(
                    lambda a: ('M' if a == 2 else 'F' if a == 1 else '') if isinstance(a, int) else a)
                users = users[np.intersect1d(self.users.columns, users.columns)]
                self.users = self.users.append(users)
                q.put((filename, counter / total))

        self.users = self.users.drop_duplicates(subset='id', keep="last")

        q.put((filename, 1))
        self.after(100, lambda: self.scrollList.remove(name=filename))

    def update_users(self, users):
        """
        Updates data on all pages
        :param users:
        :type users:
        """
        self.users = users
        if not self.profilePage:
            self.rotatingcard.updatecanvas()

    @staticmethod
    def getTime():
        """
        Returns string with current date and time
        :return:
        :rtype:
        """
        return str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

    @staticmethod
    def cleanName(name):
        """
        Removes symbols: ,.<>«»?!@:;#$%^&*/\~`'" from the given string
        :param name:
        :return:
        """
        trash = ',.<>«»?!@:;#$%^&*/\\~`\'\"|'
        filename = name
        for char in trash:
            filename = filename.replace(char, "")
        return filename

    def getMessages(self, dir, conversation, count):
        """
        Downloads messages from the given conversation and saves into the file in given directory
        :param dir:
        :param conversation:
        :param count:
        :return:
        """
        if not dir.endswith('/'):
            dir += '/'
        if conversation['conversation']['peer']['type'] == 'user':
            conversation_name = str(conversation['conversation']['peer']['id'])
            user = self.admin_apis.users.get(user_id=conversation_name)
            conversation_name += ' (' + user[0]['first_name'] + ' ' + user[0]['last_name'] + ')'
            peer_id = conversation['conversation']['peer']['local_id']
        else:
            if not ('chat_settings' in conversation['conversation']):
                print('bot, skipping...');
                return
            conversation_name = conversation['conversation']['chat_settings']['title']
            peer_id = 2000000000 + conversation['conversation']['peer']['local_id']
        offset = 0
        f = open(dir + self.cleanName(conversation_name) + '.vkmsg', "w+", True, 'UTF-8')
        f.write('[')
        while offset < count:
            tempCount = 200 if count - offset > 200 else count - offset
            history = self.admin_apis.messages.getHistory(peer_id=peer_id, count=tempCount,
                                                          offset=offset)
            attempt = 1
            while isinstance(history, Exception) and attempt < 5:
                print('Exception in getMessages sleeping..  ' + str(history.args[0]['error_msg']))
                time.sleep(2 * attempt)
                history = self.admin_apis.messages.getHistory(peer_id=peer_id, count=tempCount,
                                                              offset=offset)
                attempt = attempt + 1
            if attempt == 5:
                f.write(']')
                f.close()
                return
            if (len(history['items']) == 0):
                break
            if (offset > 0):
                f.write(',')
            f.write(json.dumps(history['items']))
            offset += tempCount
            time.sleep(0.5)
        f.write(']')
        f.close()
        return f.name

    def loadConversations(self, conversations, q):
        """
        Loads messages from given conversations and saves into file
        :param conversations:
        :type conversations:
        """
        main_dir = 'VK_Analyzer_' + self.getTime()
        os.mkdir(main_dir)
        conversationsDir = main_dir + '/conversations' + self.getTime()
        try:
            os.mkdir(conversationsDir)
        except Exception as e:
            print(e)

        conversations_count = len(conversations)
        i = 1
        print('getting conversations..')
        filenames = []
        for conversation in conversations:
            try:
                print('conversation: ' + str(i) + '/' + str(conversations_count))
                filenames.append(self.getMessages(conversationsDir, conversation, 500))
                i = i + 1
            except Exception as e:
                print('Got exception:')
                print(traceback.format_exc())
                print('working..')
                time.sleep(self.BIG_SLEEP_TIME)
        print(conversationsDir)
        q.put(filenames)
        return filenames