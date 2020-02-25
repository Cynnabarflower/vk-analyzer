import vkHacked
import time
import os
import datetime
import json
import traceback
import sys
from tkinter import *
import tkinter.messagebox
import threading


class VkLoader:

    VK_ERRORS = {
        1: {'name': 'Unknown error occurred'},
        7: {'name': 'Permission to perform this action is denied'},
        15: {'name': 'Access denied'},
        18: {'name': 'User was deleted or banned'},
        30: {'name': 'This profile is private'},
        200: {'name': 'Access to album denied'},
        201: {'name': 'Access to audio denied'},
        203: {'name': 'Access to group denied'},
        917: {'name': 'You don\'t have access to this chat'},
        936: {'name': 'Contact not found'},
        927: {'name': 'Chat does not exist'},
        29: {'name': 'Rate limit reached'}
    }

    SMALL_SLEEP_TIME = 0.1
    SLEEP_TIME = 0.5
    BIG_SLEEP_TIME = 6
    MAX_ATTEMPTS = 5
    conversations_count = 20
    msgs_count = 10000
    photo_count = 1000
    post_count = 1000
    users_count = 10000
    friends_depth = 0
    admin_api = None
    main_dir = ''
    my_id = -1
    tk_buttons = dict()
    conversations_to_load = []

    def __init__(self):
        #self.auth()
        self.createMainDir()

    def createMainDir(self):
        self.main_dir = 'VK_Analyzer_'+self.getTime()
        os.mkdir(self.main_dir)

    @staticmethod
    def cleanName(name):
        trash = ',.<>«»?!@:;#$%^&*/\\~`\'\"'
        filename = name
        for char in trash:
            filename = filename.replace(char, "")
        return filename

    def getFileName(self, name):
        name = self.cleanName(name)
        return self.main_dir+'/'+name+'_'+self.getTime()+'.txt'

    def getMessages(self, dir, conversation, count):
        if not dir.endswith('/'):
            dir += '/'
        if conversation['conversation']['peer']['type'] == 'user':
            conversation_name = str(conversation['conversation']['peer']['id'])
            user = self.admin_api.users.get(user_id=conversation_name);
            conversation_name += ' (' + user[0]['first_name'] + ' ' + user[0]['last_name'] + ')'
            peer_id = conversation['conversation']['peer']['local_id']
        else:
            if not ('chat_settings' in conversation['conversation']):
                print('bot, skipping...');
                return
            conversation_name = conversation['conversation']['chat_settings']['title']
            peer_id = 2000000000 + conversation['conversation']['peer']['local_id']
        offset = 0
        f = open(dir + self.cleanName(conversation_name) + '.txt', "w+", True, 'UTF-8')
        f.write('[')
        while offset < count:
            tempCount = 200 if count - offset > 200 else count - offset
            history = self.admin_api.messages.getHistory(peer_id=peer_id, count=tempCount, offset=offset)
            attempt = 1
            while isinstance(history, Exception) and attempt < self.MAX_ATTEMPTS:
                if (history.args[0]['error_code'] in self.VK_ERRORS):
                    print(str(history.args[0]['error_msg']))
                    f.write(']')
                    f.close()
                    return
                print('Exception in getMessages sleeping..  ' + str(history.args[0]['error_msg']))
                time.sleep(self.BIG_SLEEP_TIME * attempt)
                history = self.admin_api.messages.getHistory(peer_id=peer_id, count=tempCount, offset=offset)
                attempt = attempt + 1
            if attempt == self.MAX_ATTEMPTS:
                f.write(']')
                f.close()
                return
            if (len(history['items']) == 0):
                break
            if (offset > 0):
                f.write(',')
            f.write(json.dumps(history['items']))
            offset += tempCount
            time.sleep(self.SLEEP_TIME);
        f.write(']')
        f.close()


    @staticmethod
    def getConversationId(conversation):
        if conversation['conversation']['peer']['type'] == 'user':
            return conversation['conversation']['peer']['local_id']
        else:
            return 2000000000 + conversation['conversation']['peer']['local_id']

    def getConversationMembers(self, conversation):
        cm = self.admin_api.messages.getConversationMembers(peer_id=self.getConversationId(conversation))
        attempt = 1
        while isinstance(cm, Exception) and attempt < self.MAX_ATTEMPTS:
            if cm.args[0]['error_code'] in self.VK_ERRORS:
                print(str(cm.args[0]['error_msg']))
                return {'profiles': []}
            print('Exception in getConversationMembers sleeping.. ' + str(cm.args[0]['error_msg']))
            time.sleep(self.BIG_SLEEP_TIME * attempt)
            cm = self.admin_api.messages.getConversationMembers(peer_id=self.getConversationId(conversation))
            attempt = attempt + 1
        if attempt == self.MAX_ATTEMPTS:
            return {'profiles': []}
        return cm

    def getConversations(self, count, offset):
        conversations = self.admin_api.messages.getConversations(count=count, offset=offset);
        return conversations['items']

    def getPosts(self, owner_id, filename, count):
        f = open(filename, "w+", True, 'UTF-8')
        f.write('[')
        offset = 0
        while offset < count:
            tempCount = 200 if count - offset > 200 else count - offset
            posts = self.admin_api.wall.get(owner_id=owner_id, count=tempCount, offset=offset)
            attempt = 1
            while isinstance(posts, Exception) and attempt < self.MAX_ATTEMPTS:
                if (posts.args[0]['error_code'] in self.VK_ERRORS):
                    print(str(posts.args[0]['error_msg']))
                    return
                print('Exception in getPosts sleeping..  ' + str(posts.args[0]['error_msg']))
                time.sleep(self.BIG_SLEEP_TIME * attempt)
                posts = self.admin_api.wall.get(owner_id=owner_id, count=tempCount, offset=offset)
                attempt = attempt + 1;
            if attempt == self.MAX_ATTEMPTS:
                return
            if (offset > 0):
                f.write(',')
            f.write(json.dumps(posts['items']))
            offset += tempCount
            time.sleep(self.SLEEP_TIME);
        f.write(']')
        f.close()

    def getAlbums(self, owner_id, filename, count):
        f = open(filename, "w+", True, 'UTF-8')
        f.write('[')
        offset = 0
        while offset < count:
            tempCount = 200 if count - offset > 200 else count - offset
            photos = self.admin_api.photos.getAll(owner_id=owner_id, count=tempCount, offset=offset, extended=1)
            attempt = 1
            while isinstance(photos, Exception) and attempt < self.MAX_ATTEMPTS:
                if photos.args[0]['error_code'] in self.VK_ERRORS:
                    print(str(photos.args[0]['error_msg']))
                    return
                print('Exception in getAlbums sleeping..  ' + str(photos.args[0]['error_msg']))
                time.sleep(self.BIG_SLEEP_TIME * attempt)
                photos = self.admin_api.photos.getAll(owner_id=owner_id, count=tempCount, offset=offset, extended=1)
                attempt = attempt + 1
            if attempt == self.MAX_ATTEMPTS:
                f.write(']')
                f.close()
                return
            if len(photos['items']) == 0:
                break
            if offset > 0:
                f.write(',')
            f.write(json.dumps(photos['items']))
            offset += tempCount
            time.sleep(self.SLEEP_TIME)
        f.write(']')
        f.close()

    def __getFriendsInfo(self, user_id, depth, dictOfFriends, fields):

        friends = self.admin_api.friends.get(user_id=user_id, fields=fields)
        attempt = 1
        while isinstance(friends, Exception) and attempt < self.MAX_ATTEMPTS:
            if (friends.args[0]['error_code'] in self.VK_ERRORS):
                print(str(friends.args[0]['error_msg']))
                return
            print('Exception in getFriendsInfo sleeping..  ' + str(friends.args[0]['error_msg']))
            time.sleep(self.BIG_SLEEP_TIME * attempt)
            friends = self.admin_api.friends.get(user_id=user_id, fields=fields)
            attempt = attempt + 1
        if attempt == self.MAX_ATTEMPTS:
            return
        for friend in friends['items']:
            dictOfFriends.update({friend['id'] if 'id' in friend else friend: friend})

        if depth > 0:
            time.sleep(self.SMALL_SLEEP_TIME)
            for friend in friends['items']:
                self.__getFriendsInfo(user_id=friend['id'], depth=depth - 1, dictOfFriends=dictOfFriends, fields=fields)

    def getUserInfo(self, user_id='', filename='', user_fields = None):
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
        user = self.admin_api.users.get(user_id=user_id, fields=fields)
        attempt = 1
        while isinstance(user, Exception) and attempt < self.MAX_ATTEMPTS:
            if user.args[0]['error_code'] in self.VK_ERRORS:
                print(str(user.args[0]['error_msg']))
                return None
            print('Exception in getUserInfo sleeping..  ' + str(user.args[0]['error_msg']))
            time.sleep(self.BIG_SLEEP_TIME * attempt)
            user = self.admin_api.users.get(user_id=user_id, fields=fields)
            attempt = attempt + 1
        if attempt == self.MAX_ATTEMPTS:
            return None
        user = user[0]
        if filename:
            f = open(filename, "a", True, 'UTF-8')
            f.write(json.dumps(user))
            f.close()
        return user

    @staticmethod
    def getTime():
        return str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))


    def makeFullLoad(self, conversations = None):
        self.createMainDir()
        conversationsDir = self.main_dir + '/conversations'
        try:
            os.mkdir(conversationsDir)
        except Exception as e:
            print(e)
        usersDir = self.main_dir + '/users'
        try:
            os.mkdir(usersDir)
        except Exception as e:
            print(e)

        if not conversations:
            self.conversations_count = int(input('Number of conversations to load:\n'))
            self.friends_depth = int(input('friend depth 0 - only my friends, 1 - my and friends of my friends etc:\n'))

        print('launched: ' + self.getTime())
        print('getting friends... (depth ' + str(self.friends_depth) + ')')
        friends = self.getFriendsInfo(user_id='', user_fields=None,  depth=self.friends_depth)
        friends_len = len(friends)
        print('writing ' + str(friends_len) + ' friends... ' + self.getTime())
        i = 1
        for friend_id, friend in friends.items():
            try:
                username = str(friend_id) + ' (' + friend['first_name'] + ' ' + friend['last_name'] + ')'
                print(str(i) + ' ' + username)
                userDir = usersDir + '/' + self.cleanName(username)
                os.mkdir(userDir)
                f = open(userDir + '/info.txt', "a", True, 'UTF-8')
                f.write(json.dumps(friend))
                self.getAlbums(str(friend_id), userDir + '/photos.txt', self.photo_count)
                self.getPosts(str(friend_id), userDir + '/posts.txt', self.post_count)
                f.close()
            except Exception as e:
                print('Got exception:')
                print(traceback.format_exc())
                print('working..')
                time.sleep(self.BIG_SLEEP_TIME)
            i = i + 1

        i = 1
        print('getting conversations..')
        users = set()
        if not conversations:
            conversations = self.getConversations(self.conversations_count, 0)
        for conversation in conversations:
            try:
                print('conversation: ' + str(i) + '/' + str(self.conversations_count))
                self.getMessages(conversationsDir, conversation, self.msgs_count)
                conversationMembers = self.getConversationMembers(conversation)
                if (len(users) < self.users_count):
                    for conversationMember in conversationMembers['profiles']:
                        if ('is_closed') in conversationMember and not conversationMember['is_closed']:
                            users.add(conversationMember['id'])
                i = i + 1
            except Exception as e:
                print('Got exception:')
                print(traceback.format_exc())
                print('working..')
                time.sleep(self.BIG_SLEEP_TIME)

        print('now parsing ' + str(len(users)) + ' conversation members...')
        i = 1
        for userId in users:
            if i % 10 == 0:
                print(i)
            i = i + 1
            user = self.admin_api.users.get(user_id=userId)[0]
            username = str(user['id']) + ' (' + user['first_name'] + ' ' + user['last_name'] + ')'
            userDir = usersDir + '/' + self.cleanName(username)
            if not userId in friends:
                try:
                    os.mkdir(userDir)
                    self.getUserInfo(user['id'], userDir + '/info.txt')
                    self.getAlbums(user['id'], userDir + '/photos.txt', self.photo_count)
                    self.getPosts(user['id'], userDir + '/posts.txt', self.post_count)
                except Exception as e:
                    print('Got exception:')
                    print(traceback.format_exc())
                    print('working..')
                    time.sleep(self.BIG_SLEEP_TIME)
        print('done! ' + getTime())

    def __getOnlineList(self, user_id, depth, friends_online, friends_online_mobile):
        friends = self.admin_api.friends.getOnline(user_id=user_id, online_mobile=1)
        attempt = 1
        while isinstance(friends, Exception):
            print('in getOnlineList: ' + str(friends.args[0]['error_msg']))
            if friends.args[0]['error_code'] in self.VK_ERRORS:
                return
            time.sleep(self.BIG_SLEEP_TIME * attempt)
            friends = self.admin_api.friends.getOnline(user_id=user_id, online_mobile=1)
            attempt = attempt + 1
        friends_online.update(friends['online'])
        friends_online_mobile.update(friends['online_mobile'])
        if depth > 0:
            time.sleep(self.SLEEP_TIME)
            for friend_id in friends['online']:
                self.__getOnlineList(friend_id, depth - 1, friends_online, friends_online_mobile)
                time.sleep(self.SLEEP_TIME)

    def getOnline(self, dir='', depth=-1):
        self.main_dir = 'vkAnalyzer' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        filename = self.main_dir + '/online.txt'
        if dir:
            if os.path.isdir(dir):
                self.main_dir = dir
                filename = self.main_dir + '/online.txt'
            elif os.path.isfile(dir):
                filename = dir
        friends_online = set()
        friends_online_mobile = set()
        if depth < 0:
            depth = int(input('depth:\n'))
        print('Loading online friends... ')
        self.__getOnlineList('', depth, friends_online, friends_online_mobile)
        os.mkdir(self.main_dir)
        f = open(filename, "w+", True, 'UTF-8')
        online_string = repr(friends_online)
        online_mobile_string = repr(friends_online_mobile)
        f.write('{"online":[' + (online_string[2:len(online_string) - 2]) + '],\n')
        f.write('"online_mob":[' + (online_mobile_string[2:len(online_mobile_string) - 2]) + ']}')
        f.close()
        print('done!')
        print(filename)

    def loadConversations(self, conversations):
        self.createMainDir()
        conversationsDir = self.main_dir + '/conversations'+self.getTime()
        try:
            os.mkdir(conversationsDir)
        except Exception as e:
            print(e)

        if not conversations:
            conversations_count = int(input('Number of conversations to load:\n'))
        else:
            conversations_count = len(conversations)
        i = 1
        print('getting conversations..')
        users = set()
        if not conversations:
            conversations = self.getConversations(conversations_count, 0)
        for conversation in conversations:
            try:
                print('conversation: ' + str(i) + '/' + str(conversations_count))
                self.getMessages(conversationsDir, conversation, self.msgs_count)
                i = i + 1
            except Exception as e:
                print('Got exception:')
                print(traceback.format_exc())
                print('working..')
                time.sleep(self.BIG_SLEEP_TIME)
        print(conversationsDir)


    def getFriendsInfo(self, user_id, user_fields, depth, filename=''):
        friends = dict()
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
        if depth < 0:
            depth = int(input('depth:\n'))
        self.__getFriendsInfo(user_id, depth, friends, fields)
        if filename:
            f = open(filename, "w+", True, 'UTF-8')
            f.write(json.dumps(friends))
            f.close()
        return friends

    def auth(self, tel = '', pas = ''):
        phone = tel if tel else input('phone:')
        passw = pas if pas else input('pass:') #9841b7a33831ef01
        self.admin_api = vkHacked.VKFA(phone, passw)
        auth = self.admin_api.auth()
        if not auth:
            return False
        print(auth)
        self.my_id = self.getUserInfo('', '')['id']
        return True

    def wLastSeen(self):
        i = 0
        while i < 4 * 3:
            i = i + 1
            filename = self.getFileName('last_online')
            self.getFriendsInfo('', 'last_seen', 0, filename)
            print(i)
            print(filename)
            time.sleep(60 * 15)


    def watchLastSeen(self):
        threading.Thread(target=lambda self: self.wLastSeen(), args=([self])).start()

    def mainMenu(self):
        answers = {
            'A': {'name': ('[A]uth ' + ('' if self.admin_api is None else '(logged in: ' + self.admin_api.login + ')')), 'foo': lambda: self.auth()},
            'F': {'name': '[F]ull load', 'foo': lambda: self.makeFullLoad()},
            'O': {'name': '[O]nline friends', 'foo': lambda: self.getOnline(self.getFileName('online'), int(input('depth:')))},
            'L': {'name': '[L]ast time online', 'foo': lambda: self.getFriendsInfo('', 'last_seen', int(input('depth:')), self.getFileName('last_online'))},
            'Q': {'name': '[Q]uit', 'foo': lambda: sys.exit}
        }

        print('Main menu:')
        for ans in answers.items():
            print(ans[1]['name'])
        user_answer = input()
        if user_answer in answers:
            try:
                answers[user_answer]['foo']()
            except Exception as e:
                print(traceback.format_exc())
                print('Maybe not logged in?')

        self.mainMenu()

    def tkMenu(self):



        answers = {
            'A': {'name': ('Auth ' + ('' if self.admin_api is None else '(logged in: ' + self.admin_api.login + ')')), 'foo': lambda: auth_menu()},
            'F': {'name': 'Load conversations', 'foo': lambda: loadConversationsMenu()},
            'O': {'name': 'Online friends', 'foo': lambda: self.getOnline(self.getFileName('online'), 0)},
            'L': {'name': 'Last time online monitor (4 times/h 3h)', 'foo': lambda: self.watchLastSeen()},
            'Q': {'name': 'Quit', 'foo': lambda: sys.exit()}
        }

        def login():
            self.auth()
        root = Tk()
        root.geometry("500x400")

        def loadMainMenu():
            clear()
            for ans in answers.items():
                button = Button(bg='white', text=ans[1]['name'], command=lambda name=ans[0]: answers[name]['foo']())
                button.pack(fill=BOTH, expand=1)

        def clear():
            for widget in root.winfo_children():
                widget.pack_forget()

        def auth_menu():
            clear()
            Label(text="Tel:").pack()
            entryTel = Entry(root)
            entryTel.pack()
            Label(text="Pass:").pack()
            entryPas = Entry(root)
            entryPas.pack()
            button = Button(bg='white', text='To Menu', command=lambda: loadMainMenu())
            button.pack(fill=BOTH, expand=1)
            button = Button(bg='white', text='Auth', command=lambda: loadMainMenu() if (entryPas.get() and entryTel.get() and self.auth(tel=entryTel.get(), pas=entryPas.get())) else tkinter.messagebox.showinfo("", "Failed to login") )
            button.pack(fill=BOTH, expand=1)

        def conversation_clicked(event):
            load = not self.tk_buttons[event]['load']
            self.tk_buttons[event]['load'] = load
            self.tk_buttons[event]['button'].config(bg = 'white' if load else 'red')
            if load:
                self.conversations_to_load.append(self.tk_buttons[event]['conversation'])
            else:
                self.conversations_to_load.remove(self.tk_buttons[event]['conversation'])

        def loadConversationsMenu():
            clear()
            Label(text="Red conversations wont be loaded").pack()
            if (len(self.tk_buttons) == 0):
                conversations = self.getConversations(20, 0)
            else:
                conversations = self.tk_buttons.items()

            Button(bg='white', text='Load!',command=lambda: self.loadConversations(self.conversations_to_load) ).pack(fill=BOTH, expand=1)
            Button(bg='white', text='Back', command=lambda: loadMainMenu()).pack(fill=BOTH,expand=1)
            Label(text="Conversations:").pack()
            if len(self.tk_buttons) == 0:
                for conversation in conversations:
                    time.sleep(0.3)
                    conversation_name = False
                    peer_id = conversation['conversation']['peer']['local_id']
                    if conversation['conversation']['peer']['type'] == 'user':
                        user = self.admin_api.users.get(user_id=str(conversation['conversation']['peer']['id']))
                        conversation_name = user[0]['first_name'] + ' ' + user[0]['last_name']
                    else:
                        if ('chat_settings' in conversation['conversation']):
                            conversation_name = conversation['conversation']['chat_settings']['title']

                    if (conversation_name):
                        button = Button(bg='white', text=conversation_name, command=lambda name = conversation_name: conversation_clicked(name))
                        button.pack(fill=BOTH, expand=1)
                        self.tk_buttons.update({conversation_name : {'button': button, 'conversation': conversation, 'load': True}})
                        self.conversations_to_load.append(conversation)
            else:
                for conversation in conversations:
                    conversation[1]['button'].pack(fill=BOTH, expand=1)

        auth_menu()
        root.mainloop()

VkLoader().tkMenu()
# makeFullLoad()
# auth()
# getOnline()


