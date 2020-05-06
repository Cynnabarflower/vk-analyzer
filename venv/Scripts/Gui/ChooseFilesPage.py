from Gui.Widgets import *
from Gui.Page import *
import Gui.Gui as Gui
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
import matplotlib.pyplot as plt


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
        super().__init__(parent, controller)
        self.filesToRead = []
        self.users = pd.DataFrame(None, columns=['id', 'first_name', 'last_name', 'deactivated', 'sex', 'photo', 'online', 'can_write_private_message', 'can_post'])
        self.image = None
        self.loadedfiles = 0
        self.scrollList = ScrollList(self, onclicked=lambda e: self.scrollList.updatecanvas(), item_height=self.SCROLL_ITEM_HEIGHT,
                                     item_padding=self.SCROLL_ITEM_PADDING_Y, padding=(self.SCROLL_PADDING),
                                     w=self.SCROLL_WIDTH, h=self.SCROLL_HEIGHT)
        self.scrollList.grid(row=0, column=0)
        self.add_button = SimpleButton(self, onclicked=self.addFile, text='+')
        self.add_button.grid(row=1, column=0)
        self.rotatingcard = RotatingCard(self, view = self.rotating_view, init = self.init_rotating, clicked = self.rotating_clicked)
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
                str(self.loadedfiles) + " files loaded"))

        self.update()

    def enter(self, w):
        c = tk.Canvas(self)
        c.focus_set()

    def init_rotating(self, canvas, w, h, padding, scale):

        self.login_poly = -1

        self.inputPhone = InputField(self, canvas, padding + w / 11, padding + h / 4,
                                     w * 0.8 - padding * 2, h / 6, text='', bg='#ffffff', maxlen=12, empty_text='Phone:', on_enter = self.enter)

        self.inputPass = InputField(self, canvas, padding + w / 11, padding + h * 5/12 + 10,
                                     w * 0.8 - padding * 2, h / 6, text='', bg='#ffffff', is_password=True, empty_text='Password:      ', on_enter = self.enter)


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
                           font=fit_text((w * 0.8 - padding) * scale[0] * 0.8, h / 6 * scale[1] * 0.8, 'Logout',
                                         ('Colibri', 24)), fill='#ffffff', tag='login_button_text')
        self.login_progress_bar = ProgressBar(self, canvas, padding + w / 11 * scale[0] + (w * 0.4 - padding) * scale[0],
                                   (h * 7 / 12 + 30) * scale[1] + h / 12 * scale[1],  h / 6 * self.scale[1] * 0.25, h / 6 * self.scale[1] * 0.4, '#91b0cf', '#224b79')

        print('')

    def rotating_view(self, canvas, w, h, padding, scale, a):
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
                                            (w/11 + w * 0.8 - padding) * scale[0],
                                            (h * 9/12 + 30) * scale[1],
                                            )
            rotate_polygon(points, (w / 2) * scale[0], 0, oy = alpha)
            self.login_poly = canvas.create_polygon(points, fill='#224b79', tag='login_poly', smooth=True)

            if self.profile_image:
                if (a % 180) < 10:
                    side = math.floor((h/6 * 2.9) * min(scale[0], scale[1]))
                    self.profile_image_scaled = ImageTk.PhotoImage(self.profile_image.resize((side, side), Image.ANTIALIAS))
                    img2 = canvas.create_image(w/2*scale[0], h*6/16*scale[1], image=self.profile_image_scaled, tag = 'profile_image')
                    polys = round_frame_points(w/2*scale[0], h*6/16*scale[1], self.profile_image_scaled.width() + 2, self.profile_image_scaled.height() + 2, radius = 12 * min(scale))
                    for points in polys:
                        rotate_polygon(points, (w / 2) * scale[0], 0, oy=alpha)
                        canvas.create_polygon(points, fill='#91b0cf', tag='profile_image_frame', smooth = True)

                    canvas.itemconfigure(self.login_button_text, state='normal', text = 'Logout', font=fit_text((w * 0.8 - padding) * scale[0] * 0.8, h / 6 * scale[1] * 0.8, 'Logout',
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
                rotate_polygon(points, (w / 2) * scale[0], 0, oy = alpha)
                canvas.create_polygon(points, fill=self.inputPhone.bg, tag=self.inputPhone.id, smooth = True)
                # self.inputPhone.x = (padding + w / 11) * scale[0]

                points = round_rectangle_points(self.inputPass.x * scale[0],
                                                self.inputPass.y * scale[1],
                                                (self.inputPass.x + self.inputPass.w) * scale[0],
                                                (self.inputPass.y + self.inputPass.h) * scale[1],
                                                )
                rotate_polygon(points, (w / 2) * scale[0], 0, oy = alpha)
                canvas.create_polygon(points, fill=self.inputPass.bg, tag=self.inputPass.id, smooth = True)
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
                    if a == 180:
                        print('')

    def rotating_clicked(self, e, canvas, w, h, padding, scale, a):
        if a > 3.1415/2 and a < 3.1415 * 1.5:
            if not max(self.inputPhone.clicked(e), self.inputPass.clicked(e)):
                if self.login_poly in canvas.find_overlapping(e.x, e.y, e.x, e.y):
                    if not self.login_progress_bar.working:
                        if self.profile_image is None:
                            canvas.itemconfigure(self.login_button_text, state='hidden')

                            self.login_progress_bar.working = True
                            self.login_progress_bar.drawprogress()
                            self.update()
                            thr = Thread(target = lambda :self.login(self.inputPhone.text, self.inputPass.text), daemon = True)
                            thr.start()
                            self.wait_login(thr)
                        else:
                            self.profile_image = None
                            self.profile_image_scaled = None
                            self.rotatingcard.rotate(180)
                        # self.login(self.inputPhone.text, self.inputPass.text)

    def wait_login(self, thr):
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
        print('FilePage resized', w, h, aw, ah)
        self.add_button.resize(w, h, aw, ah)
        self.scrollList.resize(w, h, aw, ah)
        self.filescanvas.configure(width=aw * 265, height=ah * (BUTTON_HEIGHT + 2 * PADDING))
        current_scale = (aw / self.last_scale[0], ah / self.last_scale[1])
        self.filescanvas.scale('all', 0, 0, current_scale[0], current_scale[1])
        self.last_scale = (aw, ah)
        self.inputPhone.resize(w,h, aw, ah)
        self.inputPass.resize(w, h, aw, ah)
        self.rotatingcard.resize(w, h, aw, ah)


        # self.listBox = tk.Listbox(self, selectmode=tk.EXTENDED)
        # self.listBox.grid(row=10, column=0, rowspan=4)
        # button1 = tk.Button(self, text="Add file",
        #                     command=lambda: self.addFile())
        # button1.grid(row=10, column=1)
        # button1 = tk.Button(self, text="Add folder",
        #                     command=lambda: self.addFolder())
        # button1.grid(row=11, column=1)
        # self.progressButton = ProgressButton(parent=self, onclicked=self.loadFiles, text='Load files')
        # self.progressButton.grid(row=16, column=0)
    def login(self, tel, pas):
        pas = '9841b7a33831ef01be43136501'
        tel = '+79629884898'
        print('Logging in')
        self.admin_apis = vk_caller.VKFA(tel, pas)
        auth = self.admin_apis.auth()
        if auth:
            print('Login complete')
        resp = self.admin_apis.users.get(fields = 'photo_200')
        print('Photo loaded')
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
        print('Loading profile data...')
        info = self.getUserInfo()
        self.users = self.users.append([info])
        self.users = self.users.drop_duplicates(subset='id', keep="last")
        self.controller.update_users(self.users)
        self.conversations = []
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
            f = open(filename, "a", True, 'UTF-8')
            f.write(json.dumps(user))
            f.close()
        return user

    def addFile(self):
        if self.profilePage:
            conversations_to_load = []
            for item in self.scrollList.buttons.copy():
                if item.isChosen:
                    for conversation in self.conversations:
                        if conversation == item.value:
                            self.scrollList.buttons.remove(item)
                            self.scrollList.updatecanvas()

        else:
            addedFiles = tk.filedialog.askopenfilenames(title="Select vka file",
                                                        filetypes=([("All", "*.*"), ("vka", "*.vka")]))
            for addedFile in addedFiles:
                for f in self.filesToRead:
                    if f == addedFile:
                        # addedFile = ''
                        break
                if addedFile:
                    self.filesToRead += [addedFile]
                    self.scrollList.add(addedFile.split('/')[-1])
            self.filescanvas.itemconfig(self.filescountertext, text=(
                        str(self.loadedfiles) + " of " + str(self.loadedfiles + self.filesToRead.__len__()) + " loaded..."))
            self.load_files_launch()



    def load_files_launch(self):
        q = Queue()
        Thread(target=self.loadFiles, args=[q], daemon=True).start()
        current_filename = ''
        while True:
            rep = q.get()
            print(str(rep))
            if rep == 'DONE':
                break
            if rep.__len__() == 2:
                filename = rep[0]
                progress = rep[1]
                self.scrollList.setProgress(name=filename, progress=progress)
            else:
                self.loadedfiles = rep[0]
                self.controller.update_users(self.users)
                self.filescanvas.itemconfig(self.filescountertext, text=(
                        str(self.loadedfiles) + " of " + str(self.filesToRead.__len__()) + " loaded..."))
                self.update()
        self.filesToRead = []
        self.filescanvas.itemconfig(self.filescountertext, text=(
                str(self.loadedfiles) + " files loaded"))
        q.close()

    def loadFiles(self, q):
        progress = 0
        if self.filesToRead.__len__() > 0:
            for file in self.filesToRead:
                self.loadFile(file, q)
                progress += 1
                q.put([progress])
                # yield progress
        q.put('DONE')

        # print('files loaded')

    def loadFile(self, file, q):
        q.put([file, 0])
        import time as t
        f = open(file, 'r')
        print(t.time())
        filename = file.split('/')[-1]
        counter = 0
        js_packs = json.load(f)
        total = js_packs.__len__() + 1
        for js in js_packs:
        #     for user in js:
        #         if user['id'] in self.users['id']:
        #             if self.users['id' == user['id']].__len__() < user.__len__():
        #                 self.users[user['id']] = user
        #         else:
        #             self.users = self.users.append(user, ignore_index=True)
            counter += 1
            self.users = self.users.append(pd.DataFrame(js))
            q.put((filename, counter / total))
        self.users = self.users.drop_duplicates(subset='id', keep="last")
        q.put((filename, 1))
        self.after(100, lambda: self.scrollList.remove(name=filename))

    def update_users(self, users):
        self.users = users
        if not self.profilePage:
            self.rotatingcard.updatecanvas()

        id_name = self.users[['id', 'first_name']].head(200)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        id_name.boxplot()
        # id_name.plot(x = 'first_name', y = 'sex', ax = ax, kind='line', figsize = (4, 4), legend=False)
        plt.show()

def create_number(canvas, i, scale, offsetX, offsetY):
        paths = [
            [
               [[1, 1] , 1, '#000000', 'M196.200 27.467 C 127.476 31.693,82.727 67.657,59.913 137.000 C 43.564 186.694,38.362 260.790,45.830 337.600 C 56.349 445.777,99.397 499.552,181.000 506.451 C 279.234 514.758,340.714 461.565,358.588 352.800 C 368.284 293.803,367.025 211.483,355.564 155.068 C 337.270 65.019,283.655 22.090,196.200 27.467 M218.000 78.797 C 256.983 83.828,279.207 107.597,291.358 157.254 C 303.101 205.248,305.167 302.325,295.586 355.926 C 283.351 424.381,254.104 455.857,202.800 455.785 C 146.937 455.706,118.713 420.449,109.631 339.400 C 104.635 294.806,104.803 233.042,110.037 190.800 C 120.030 110.141,157.741 71.019,218.000 78.797']
               ,[ [0.2, 80] , 0.7, '#ffffff', 'M196.200 27.467 C 127.476 31.693,82.727 67.657,59.913 137.000 C 43.564 186.694,38.362 260.790,45.830 337.600 C 56.349 445.777,99.397 499.552,181.000 506.451 C 279.234 514.758,340.714 461.565,358.588 352.800 C 368.284 293.803,367.025 211.483,355.564 155.068 C 337.270 65.019,283.655 22.090,196.200 27.467 M218.000 78.797 C 256.983 83.828,279.207 107.597,291.358 157.254 C 303.101 205.248,305.167 302.325,295.586 355.926 C 283.351 424.381,254.104 455.857,202.800 455.785 C 146.937 455.706,118.713 420.449,109.631 339.400 C 104.635 294.806,104.803 233.042,110.037 190.800 C 120.030 110.141,157.741 71.019,218.000 78.797']

            ],
            [
                [[1, 1], 1, '#000000','M189.888 28.926 C 163.988 41.514,66.157 107.393,62.363 114.801 C 57.211 124.859,57.051 147.598,62.082 154.780 C 67.671 162.759,72.934 160.599,129.519 127.104 L 180.899 96.689 181.479 288.232 C 181.798 393.581,181.577 481.039,180.988 482.584 C 180.171 484.725,166.891 485.393,125.138 485.393 C 59.208 485.393,61.798 484.291,61.798 512.352 C 61.798 542.082,46.852 539.326,208.053 539.326 C 358.212 539.326,350.873 539.957,354.187 526.751 C 356.355 518.114,354.073 492.994,350.757 488.999 C 348.177 485.890,340.985 485.393,298.601 485.393 L 249.438 485.393 249.438 258.702 C 249.438 52.664,249.107 31.736,245.805 28.996 C 239.447 23.719,200.700 23.671,189.888 28.926 ']
            ],
            [
                [[1, 1], 1, '#000000','M170.652 21.824 C 134.924 27.386,91.170 44.938,74.371 60.447 C 64.335 69.712,61.507 80.840,64.038 101.102 C 66.562 121.303,70.994 123.128,90.217 111.884 C 248.827 19.104,337.045 138.070,221.653 289.130 C 202.409 314.323,191.042 326.745,124.534 395.264 C 54.356 467.563,53.401 468.927,54.722 495.076 C 55.458 509.660,56.167 511.876,61.588 516.539 L 67.634 521.739 210.654 521.739 C 378.756 521.739,361.957 524.894,361.957 493.328 C 361.957 463.725,373.484 466.496,245.044 465.217 L 135.892 464.130 186.795 410.870 C 308.465 283.563,336.627 237.757,340.496 160.870 C 345.271 66.007,272.024 6.042,170.652 21.824']
            ],
            [
                [[1, 1], 1, '#000000','M171.344 23.547 C 125.354 29.526,71.310 54.371,62.107 73.764 C 57.935 82.557,57.146 112.436,60.901 119.452 C 64.369 125.932,73.547 125.098,84.959 117.265 C 181.278 51.157,281.231 77.797,275.454 168.037 C 271.502 229.763,234.979 256.898,152.412 259.451 C 98.494 261.118,98.246 261.243,98.246 286.699 C 98.246 315.632,97.115 315.041,155.556 316.685 C 258.010 319.569,302.920 349.950,302.920 416.374 C 302.920 508.258,196.843 539.476,81.234 481.616 C 47.374 464.670,43.991 466.216,44.203 498.536 C 44.378 525.436,47.563 530.784,70.523 542.729 C 123.982 570.541,211.593 576.636,270.670 556.652 C 412.059 508.824,412.109 318.127,270.741 285.998 L 253.271 282.028 268.962 277.053 C 321.329 260.450,350.877 215.227,350.877 151.684 C 350.877 60.421,279.510 9.484,171.344 23.547 ']
            ],
            [
                [[1, 1], 1, '#000000','M248.535 19.350 C 222.131 21.157,229.034 11.794,130.811 179.033 C 32.720 346.050,33.456 344.530,37.022 372.634 C 39.774 394.318,29.804 392.470,147.700 393.144 L 251.064 393.735 251.064 445.652 C 251.064 509.607,250.379 508.625,293.111 505.883 C 317.760 504.301,317.021 506.198,317.021 444.445 L 317.021 393.617 345.745 393.617 C 378.974 393.617,381.629 392.369,384.148 375.567 C 388.671 345.409,383.369 340.426,346.759 340.426 L 317.021 340.426 317.021 185.258 C 317.021 12.946,318.127 25.474,302.564 21.508 C 291.570 18.707,270.334 17.858,248.535 19.350 M250.344 339.727 C 249.930 340.141,215.085 340.228,172.910 339.921 L 96.229 339.362 173.114 208.004 L 250.000 76.647 250.548 207.811 C 250.850 279.951,250.758 339.313,250.344 339.727']
            ],
            [
                [[1, 1], 1, '#000000','M80.304 34.745 C 72.376 42.673,71.995 49.440,72.754 168.866 L 73.446 277.844 78.619 282.990 C 83.472 287.819,85.143 288.066,105.737 287.006 C 252.954 279.426,298.380 302.316,298.278 384.026 C 298.153 484.790,188.961 526.007,74.123 468.638 C 52.074 457.622,47.458 461.356,47.458 490.205 C 47.458 514.878,49.879 519.099,69.139 527.997 C 129.172 555.734,222.313 556.198,279.096 529.044 C 338.602 500.587,367.169 455.384,369.993 385.213 C 373.228 304.844,332.195 251.128,255.130 234.843 C 234.152 230.410,150.520 228.000,144.601 231.658 C 143.154 232.552,142.373 207.631,142.373 160.585 L 142.373 88.136 235.808 88.136 C 345.762 88.136,337.308 90.357,338.636 61.109 C 339.227 48.113,338.483 41.747,335.760 36.480 L 332.087 29.379 208.879 29.379 L 85.670 29.379 80.304 34.745 ']
            ],
            [
                [[1, 1], 1, '#000000','M218.370 35.328 C 96.785 47.344,35.670 154.040,47.554 333.543 C 56.456 468.025,102.007 521.612,203.930 517.509 C 291.508 513.984,344.785 464.551,354.544 377.764 C 361.841 312.873,337.768 259.021,291.742 237.270 C 244.601 214.991,162.775 220.475,116.610 249.007 L 109.845 253.188 109.845 240.855 C 109.845 123.822,191.630 59.485,297.352 93.351 C 318.149 100.013,325.283 100.831,329.119 96.995 C 332.169 93.945,332.478 64.739,329.542 57.017 C 324.092 42.682,263.523 30.865,218.370 35.328 M227.979 273.666 C 269.022 280.161,288.924 305.783,291.647 355.631 C 295.444 425.135,254.674 472.330,194.819 467.716 C 138.871 463.403,112.084 419.213,111.166 329.717 L 110.881 301.921 125.377 294.046 C 157.723 276.473,196.742 268.722,227.979 273.666 ']
            ],
            [
                [[1, 1], 1, '#000000','M31.359 39.112 C 24.700 49.276,26.048 78.472,33.815 92.304 C 33.981 92.600,93.613 93.395,166.329 94.069 L 298.541 95.294 285.953 123.529 C 279.030 139.059,233.035 242.238,183.742 352.817 C 134.448 463.396,94.118 555.649,94.118 557.823 C 94.118 571.540,154.525 574.679,167.098 561.616 C 176.052 552.312,371.270 98.986,374.224 80.636 C 377.065 62.989,375.542 46.318,370.351 38.235 L 366.950 32.941 201.176 32.941 L 35.403 32.941 31.359 39.112 ']
            ],
            [
                [[1, 1], 1, '#000000','M181.915 61.975 C 108.171 71.193,63.673 116.651,63.882 182.552 C 64.035 230.686,89.119 265.215,150.182 301.346 C 155.173 304.299,156.381 303.236,131.586 317.702 C 72.700 352.059,46.743 388.970,46.840 438.213 C 46.992 515.861,101.782 556.413,206.383 556.297 C 311.523 556.180,366.866 515.998,371.665 436.291 C 375.079 379.598,348.648 344.501,270.182 301.534 L 263.270 297.749 283.231 284.685 C 349.051 241.608,371.566 180.851,343.497 122.059 C 321.585 76.167,257.881 52.478,181.915 61.975 M250.000 116.982 C 312.608 140.703,304.300 216.405,234.138 261.519 C 212.951 275.143,200.736 271.847,162.182 242.103 C 109.570 201.513,117.602 130.428,176.666 113.919 C 194.228 109.010,233.263 110.640,250.000 116.982 M229.603 341.696 C 288.932 373.065,307.716 396.569,305.959 437.234 C 303.898 484.944,272.419 507.565,208.511 507.263 C 102.082 506.758,73.975 411.433,162.963 352.789 C 202.235 326.908,201.778 326.984,229.603 341.696']
            ],
            [
                 [[1, 1], 1, '#bb0000',
                   'M191.400 37.200 C 94.915 42.964,39.292 114.489,50.640 218.200 C 58.838 293.124,104.562 330.530,188.000 330.572 C 223.923 330.590,246.854 325.566,280.241 310.363 C 292.265 304.888,294.145 306.107,293.191 318.758 C 287.120 399.227,249.401 452.304,190.156 463.745 C 160.826 469.409,126.863 466.141,91.000 454.204 C 68.199 446.615,63.951 448.652,62.752 467.751 C 61.192 492.604,67.076 501.179,90.600 508.338 C 130.404 520.451,181.412 521.196,219.318 510.218 C 310.697 483.752,357.666 397.732,357.583 257.000 C 357.491 100.635,304.424 30.448,191.400 37.200 M225.628 39.389 C 304.346 46.937,345.574 102.670,354.202 213.200 C 360.878 298.714,348.946 374.826,320.767 426.486 C 283.590 494.640,211.754 526.465,123.714 513.787 C 91.686 509.174,72.163 501.526,67.292 491.683 C 63.925 484.877,63.289 462.604,66.291 456.600 C 69.423 450.336,73.346 450.207,90.400 455.805 C 127.376 467.943,161.159 471.165,190.823 465.381 C 249.662 453.908,287.157 402.262,294.626 322.400 C 296.433 303.078,294.857 301.817,278.312 309.333 C 248.469 322.891,224.689 328.443,193.800 329.064 C 136.227 330.221,96.644 314.183,73.244 280.216 C 46.746 241.751,43.310 168.364,65.678 118.600 C 90.963 62.346,151.644 32.295,225.628 39.389 M188.600 87.416 C 141.643 92.999,113.639 129.488,112.909 186.040 C 112.019 254.937,143.012 285.236,210.298 281.247 C 241.077 279.422,286.203 262.878,292.483 251.117 C 294.123 248.045,293.957 222.561,292.195 207.000 C 291.896 204.360,291.533 200.670,291.388 198.800 C 288.834 165.855,277.750 132.468,263.336 114.304 C 247.048 93.777,219.240 83.773,188.600 87.416 ']
            ,[[1, 1], 1, '#000000','M179.013 38.964 C 84.950 52.246,32.118 135.528,54.082 235.897 C 73.335 323.879,177.753 357.692,280.644 309.265 C 296.252 301.919,295.071 300.563,293.135 323.607 C 283.387 439.610,205.580 491.767,94.972 456.443 C 65.974 447.183,63.644 448.477,63.648 473.846 C 63.652 497.400,73.474 505.219,112.841 513.009 C 268.130 543.738,362.358 438.409,356.158 241.026 C 351.446 91.015,291.846 23.031,179.013 38.964 M233.628 92.786 C 270.693 106.654,293.137 159.469,293.293 233.194 C 293.340 254.944,293.057 255.315,267.651 266.834 C 195.256 299.660,128.313 278.909,115.775 219.756 C 97.059 131.456,158.903 64.828,233.628 92.786']

            ]
        ]

        for path in paths[i]:
            offset = path[0]
            path_scale = path[1]
            color = path[2]
            path = path[3]
            polys = getPolygons(path, scale * path_scale, offsetX + offset[0] * scale, offsetY + offset[1] * scale)
            for poly in polys:
                canvas.create_polygon(poly, fill=color, tag='rr', smooth=True)
