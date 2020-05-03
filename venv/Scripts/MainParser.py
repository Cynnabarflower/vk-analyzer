import vk_caller
import time
import os
import datetime
import json
import traceback
import sys
from tkinter import *
import tkinter.messagebox
import threading
import requests


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
    admin_apis = [None, ]
    current_acc = 0
    main_dir = ''
    my_id = -1
    tk_buttons = dict()
    conversations_to_load = []

    def __init__(self):
        # self.auth()
        self.createMainDir()

    def createMainDir(self):
        """
        Creates a directory for current launch
        """
        self.main_dir = 'VK_Analyzer_' + self.getTime()
        os.mkdir(self.main_dir)

    @staticmethod
    def cleanName(name):
        """
        Removes symbols: ,.<>«»?!@:;#$%^&*/\~`'" from the given string
        :param name:
        :return:
        """
        trash = ',.<>«»?!@:;#$%^&*/\\~`\'\"'
        filename = name
        for char in trash:
            filename = filename.replace(char, "")
        return filename

    def getFileName(self, name):
        """
        Returns a valid filename in current launch directory based on given name
        :param name:
        :return:
        """
        name = self.cleanName(name)
        return self.main_dir + '/' + name + '_' + self.getTime() + '.txt'

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
            user = self.admin_apis[self.current_acc].users.get(user_id=conversation_name);
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
            history = self.admin_apis[self.current_acc].messages.getHistory(peer_id=peer_id, count=tempCount,
                                                                            offset=offset)
            attempt = 1
            while isinstance(history, Exception) and attempt < self.MAX_ATTEMPTS:
                if (history.args[0]['error_code'] in self.VK_ERRORS):
                    print(str(history.args[0]['error_msg']))
                    f.write(']')
                    f.close()
                    return
                print('Exception in getMessages sleeping..  ' + str(history.args[0]['error_msg']))
                time.sleep(self.BIG_SLEEP_TIME * attempt)
                history = self.admin_apis[self.current_acc].messages.getHistory(peer_id=peer_id, count=tempCount,
                                                                                offset=offset)
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
        """
        Returns conversation id
        :param conversation:
        :return:
        """
        if conversation['conversation']['peer']['type'] == 'user':
            return conversation['conversation']['peer']['local_id']
        else:
            return 2000000000 + conversation['conversation']['peer']['local_id']

    def getConversationMembers(self, conversation):
        """
        Returns list of conversation members
        :param conversation:
        :return:
        """
        cm = self.admin_apis[self.current_acc].messages.getConversationMembers(
            peer_id=self.getConversationId(conversation))
        attempt = 1
        while isinstance(cm, Exception) and attempt < self.MAX_ATTEMPTS:
            if cm.args[0]['error_code'] in self.VK_ERRORS:
                print(str(cm.args[0]['error_msg']))
                return {'profiles': []}
            print('Exception in getConversationMembers sleeping.. ' + str(cm.args[0]['error_msg']))
            time.sleep(self.BIG_SLEEP_TIME * attempt)
            cm = self.admin_apis[self.current_acc].messages.getConversationMembers(
                peer_id=self.getConversationId(conversation))
            attempt = attempt + 1
        if attempt == self.MAX_ATTEMPTS:
            return {'profiles': []}
        return cm

    def getConversations(self, count, offset):
        """
        Returns list of conversation objects for current user
        :param count:
        :param offset:
        :return:
        """

        count = 200
        conversations = self.admin_apis[self.current_acc].messages.getConversations(count=count, offset=offset);
        return conversations['items']

    def getPosts(self, owner_id, filename, count):
        """
        Downloads owner's posts and saves into given filename
        :param owner_id:
        :type owner_id:
        :param filename:
        :type filename:
        :param count:
        :type count:
        :return:
        :rtype:
        """
        f = open(filename, "w+", True, 'UTF-8')
        f.write('[')
        offset = 0
        while offset < count:
            tempCount = 200 if count - offset > 200 else count - offset
            posts = self.admin_apis[self.current_acc].wall.get(owner_id=owner_id, count=tempCount, offset=offset)
            attempt = 1
            while isinstance(posts, Exception) and attempt < self.MAX_ATTEMPTS:
                if (posts.args[0]['error_code'] in self.VK_ERRORS):
                    print(str(posts.args[0]['error_msg']))
                    return
                print('Exception in getPosts sleeping..  ' + str(posts.args[0]['error_msg']))
                time.sleep(self.BIG_SLEEP_TIME * attempt)
                posts = self.admin_apis[self.current_acc].wall.get(owner_id=owner_id, count=tempCount, offset=offset)
                attempt = attempt + 1;
            if attempt == self.MAX_ATTEMPTS:
                return
            if (offset > 0):
                f.write(',')
            f.write(json.dumps(posts['items']))
            offset += tempCount
            time.sleep(self.SLEEP_TIME)
        f.write(']')
        f.close()

    def getAlbums(self, owner_id, filename, count):
        """
        Downloads names and links of owners albums and photos and saves into given file
        :param owner_id:
        :type owner_id:
        :param filename:
        :type filename:
        :param count:
        :type count:
        :return:
        :rtype:
        """
        f = open(filename, "w+", True, 'UTF-8')
        f.write('[')
        offset = 0
        while offset < count:
            tempCount = 200 if count - offset > 200 else count - offset
            photos = self.admin_apis[self.current_acc].photos.getAll(owner_id=owner_id, count=tempCount, offset=offset,
                                                                     extended=1)
            attempt = 1
            while isinstance(photos, Exception) and attempt < self.MAX_ATTEMPTS:
                if photos.args[0]['error_code'] in self.VK_ERRORS:
                    print(str(photos.args[0]['error_msg']))
                    return
                print('Exception in getAlbums sleeping..  ' + str(photos.args[0]['error_msg']))
                time.sleep(self.BIG_SLEEP_TIME * attempt)
                photos = self.admin_apis[self.current_acc].photos.getAll(owner_id=owner_id, count=tempCount,
                                                                         offset=offset, extended=1)
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
        """
        SHOULD NOT BE USED (see getFriendsInfo)
        :param user_id:
        :type user_id:
        :param depth:
        :type depth:
        :param dictOfFriends:
        :type dictOfFriends:
        :param fields:
        :type fields:
        :return:
        :rtype:
        """
        dictOfFriends[user_id]['isLoaded'] = True
        friends = self.admin_apis[self.current_acc].friends.get(user_id=user_id, fields=fields)
        attempt = 1
        while isinstance(friends, Exception) and attempt < self.MAX_ATTEMPTS:
            if (friends.args[0]['error_code'] in self.VK_ERRORS):
                print(str(friends.args[0]['error_msg']))
                return
            print('Exception in getFriendsInfo sleeping..  ' + str(friends.args[0]['error_msg']))
            time.sleep(self.BIG_SLEEP_TIME * attempt)
            friends = self.admin_apis[self.current_acc].friends.get(user_id=user_id, fields=fields)
            attempt = attempt + 1
        if attempt == self.MAX_ATTEMPTS:
            return
        c_time = time.time()
        for friend in friends['items']:
            if not (friend['id'] if 'id' in friend else friend) in dictOfFriends:
                friend['scan_time'] = c_time
                dictOfFriends.update({friend['id'] if 'id' in friend else friend: friend})

        print(depth, ' got: ', len(dictOfFriends), self.getTime())
        if depth > 0:
            time.sleep(self.SMALL_SLEEP_TIME)
            for friend in friends['items']:
                cId = friend['id']
                if 'isLoaded' in dictOfFriends[cId] and dictOfFriends[cId]['isLoaded']:
                    print('Already have this one')
                    continue
                else:
                    self.__getFriendsInfo(user_id=cId, depth=depth - 1, dictOfFriends=dictOfFriends, fields=fields)
                    time.sleep(self.SMALL_SLEEP_TIME)

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
        user = self.admin_apis[self.current_acc].users.get(user_id=user_id, fields=fields)
        attempt = 1

        while isinstance(user, Exception) and attempt < self.MAX_ATTEMPTS:
            if user.args[0]['error_code'] in self.VK_ERRORS:
                print(str(user.args[0]['error_msg']))
                return None
            print('Exception in getUserInfo sleeping..  ' + str(user.args[0]['error_msg']))
            time.sleep(self.BIG_SLEEP_TIME * attempt)
            user = self.admin_apis[self.current_acc].users.get(user_id=user_id, fields=fields)
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
        """
        Returns string with current date and time
        :return:
        :rtype:
        """
        return str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

    def makeFullLoad(self, conversations=None):
        """
        Loads messages from given conversations, then
        information, posts and photos from members of those conversations.
        All the information saved in main launch folder
        :param conversations:
        :type conversations:
        """
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
        friends = self.getFriendsInfo(user_id='', user_fields=None, depth=self.friends_depth)
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
            except Exception as    e:
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
            user = self.admin_apis[self.current_acc].users.get(user_id=userId)[0]
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
        """
        SHOULD NOT BE USED (see getOnlineList)
        :param user_id:
        :type user_id:
        :param depth:
        :type depth:
        :param friends_online:
        :type friends_online:
        :param friends_online_mobile:
        :type friends_online_mobile:
        :return:
        :rtype:
        """
        friends = self.admin_apis[self.current_acc].friends.getOnline(user_id=user_id, online_mobile=1)
        attempt = 1
        while isinstance(friends, Exception):
            print('in getOnlineList: ' + str(friends.args[0]['error_msg']))
            if friends.args[0]['error_code'] in self.VK_ERRORS:
                return
            time.sleep(self.BIG_SLEEP_TIME * attempt)
            friends = self.admin_apis[self.current_acc].friends.getOnline(user_id=user_id, online_mobile=1)
            attempt = attempt + 1
        friends_online.update(friends['online'])
        friends_online_mobile.update(friends['online_mobile'])
        if depth > 0:
            time.sleep(self.SLEEP_TIME)
            for friend_id in friends['online']:
                self.__getOnlineList(friend_id, depth - 1, friends_online, friends_online_mobile)
                time.sleep(self.SLEEP_TIME)

    def getOnline(self, dir='', depth=-1):
        """
        Loads information about users online and saves in a new file in given dir.
        users are:
         friends (depth = 0)
         friends and their friends (depth = 1)
         etc
         waits for input if depth < 0
        :param dir:
        :type dir:
        :param depth:
        :type depth:
        """
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
        print(self.getTime())
        print(filename)

    def loadConversations(self, conversations):
        """
        Loads messages from given conversations and saves into file
        :param conversations:
        :type conversations:
        """
        self.createMainDir()
        conversationsDir = self.main_dir + '/conversations' + self.getTime()
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

    def change_account(self):
        self.current_acc = (self.current_acc + 1) % self.admin_apis.__len__()
        print('Account changed to', self.current_acc)

    def getFromGroup(self, group_name, maxMembers=-1, user_fields=None, offset=0, apis = None):
        """
        Finds group by name and loads full info about it's members
        :param group_name:
        :type group_name:
        :param maxMembers:
        :type maxMembers:
        :return:
        :rtype:
        """

        fields = 'nickname, screen_name, sex, bdate, city, country, timezone, photo, has_mobile, contacts, education, online, counters, relation, last_seen, activity, can_write_private_message, can_see_all_posts, can_post, universities, followers_count, counters, occupation'
        if not (user_fields is None):
            if isinstance(user_fields, str):
                fields = user_fields
            elif isinstance(user_fields, list):
                fields = str(user_fields)[1::][:-1].replace("'", "").replace('"', '')
            else:
                print('Incorrect user fields, should be str')
                return

        current_acc = 0
        if not apis:
            apis = self.admin_apis
            current_acc = self.current_acc

        group = apis[current_acc].groups.getById(group_id=group_name, fields="members_count")
        print('getting from group ', group[0]['name'], '...')
        group_id = group[0]['id']
        members_count = group[0]['members_count']
        if maxMembers > 0:
            members_count = min(members_count, maxMembers)
        execString = "return "
        call_count = 0
        members = []
        time.sleep(self.SMALL_SLEEP_TIME)
        while members_count > offset:
            while call_count < 16:
                if call_count:
                    execString += "+"
                execString += ("API.users.get({'user_ids':API.groups.getMembers({'group_id':"
                               + str(group_id) + ",'offset':" + str(offset) +
                               ",'count':" + str(min(members_count - offset, 1000)) +
                               "}).items,'fields':'" + fields + "'}) ")
                call_count += 2
                offset += min(members_count - offset, 1000)
                if offset >= members_count:
                    break
            c_time = time.time()
            resp = apis[current_acc].execute(code=execString + ';')
            attempt = 1
            while isinstance(resp, Exception) and attempt < self.MAX_ATTEMPTS:
                if isinstance(resp, requests.exceptions.RequestException):
                    print('ConnectionError waiting 10 min')
                    resp = apis[current_acc].execute(code=execString + ';')
                    time.sleep(self.BIG_SLEEP_TIME * 10 * 10)
                    attempt = 1
                    continue
                elif(resp.args.__len__() > 0):
                    if isinstance(resp.args[0] , str):
                        print(resp.args[0])
                        time.sleep(self.BIG_SLEEP_TIME * attempt)
                        resp = apis[current_acc].execute(code=execString + ';')
                        attempt = attempt + 5
                        continue

                    elif (resp.args[0]['error_code'] in self.VK_ERRORS):
                        if resp.args[0]['error_code'] == 29:
                            current_acc = (current_acc + 1) % apis.__len__()
                            # self.change_account()
                        else:
                            print(str(history.args[0]['error_msg']))
                            f.write(']')
                            f.close()
                    else:
                        print('Exception in getMessages sleeping..  ' + str(resp.args[0]['error_msg']))
                        time.sleep(self.BIG_SLEEP_TIME * attempt)
                        resp = apis[current_acc].execute(code=execString + ';')
                        attempt = attempt + 3
                else:
                    print('Exception in getMessages sleeping..  ',resp.args)
                    time.sleep(self.BIG_SLEEP_TIME * attempt)
                    resp = apis[current_acc].execute(code=execString + ';')
                    attempt = attempt + 5

            if isinstance(resp, Exception):
                return members

            for user in resp:
                user['scan_time'] = c_time
            members.append(resp)
            execString = "return "
            call_count = 0
            print('got: ', offset, '/', members_count)
            if offset < members_count:
                time.sleep(self.SLEEP_TIME)
        print(apis[current_acc], group_name, 'done!')
        return members

    def saveToFile(self, obj, name):
        """
        Creates a file based on name in current launch directory and saves object as json
        :param obj:
        :type obj:
        :param name:
        :type name:
        """
        filename = self.getFileName(name)
        f = open(filename, "w+", True, 'UTF-8')
        f.write(json.dumps(obj))
        f.close()
        # print('File saved: ', filename)

    def getFriendsInfo(self, user_id, user_fields, depth, filename=''):
        """
        Loads information about friends (depth = 0) of give user and returns or,
        if filename is given, saves to file.
        if (depth = 1) loads information about frineds and their frineds, etc
        if (depth < 0) waits for input
        :param user_id:
        :type user_id:
        :param user_fields:
        :type user_fields:
        :param depth:
        :type depth:
        :param filename:
        :type filename:
        :return:
        :rtype:
        """
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
        try:
            friends.update({user_id: dict()})
            self.__getFriendsInfo(user_id, depth, friends, fields)
        except Exception as e:
            print(traceback.format_exc())

        if filename:
            f = open(filename, "w+", True, 'UTF-8')
            f.write(json.dumps(friends))
            f.close()
        return friends

    def init_load_groups(self):

        apis = [
            vk_caller.VKFA('+77053909746', '123456zxcvb'),
            vk_caller.VKFA('+79091758992','evolom08ASDfghjkl')
        ]
        for api in apis:
            api.auth()
        threading.Thread(target=lambda :self.load_groups(apis = apis)).start()
        time.sleep(60*60)
        apis = [
            vk_caller.VKFA('crazytuner@freenet.de','oberhase64'),
        ]
        for api in apis:
            api.auth()
        threading.Thread(target=lambda :self.load_groups(apis = apis)).start()
        time.sleep(60 * 60)
        apis = [
            vk_caller.VKFA('+79285474003','s.r.81104'),
            vk_caller.VKFA('+79886828338', 'EGUMES54')
        ]
        for api in apis:
            api.auth()
        threading.Thread(target=lambda :self.load_groups(apis = apis)).start()
        time.sleep(60 * 60)
        apis = [
            vk_caller.VKFA('89083004616', 'RTE34213421')
        ]
        for api in apis:
            api.auth()
        threading.Thread(target=lambda: self.load_groups(apis=apis)).start()

    def auth(self, tel='', pas=''):
        """
        Authorization by phone and password in vk
        :param tel:
        :type tel:
        :param pas:
        :type pas:
        :return:
        :rtype:
        """

        # pas = '9841b7a33831ef01be43136501'
        # tel = '+79629884898'
        phone = tel if tel else input('phone:')
        passw = pas if pas else input('pass:')  # 9841b7a33831ef01
        self.admin_apis[self.current_acc] = vk_caller.VKFA(phone, passw)
        auth = self.admin_apis[self.current_acc].auth()
        if not auth:
            return False
        print(auth)
        return True
        self.admin_apis.insert(1, vk_caller.VKFA('+15102750266', 'wZigy4cuHNi4KQy'))
        auth = self.admin_apis[1].auth()
        print(auth)
        self.my_id = self.getUserInfo('', '')['id']
        return True

    def wLastSeen(self):
        """
        Saves into a new file in main launch directory base information about all online friends of current user,
         and their online friends for 12 hours every 15 minutes.
        """
        i = 0
        print('Last seen...')
        while i < 4 * 12:
            try:
                i = i + 1
                filename = self.getFileName('last_  online')
                self.getFriendsInfo(self.getUserInfo()['id'], 'last_seen', 1, filename)
                print(i)
                print(filename)
                time.sleep(60 * 15)
            except Exception as e:
                print(traceback.format_exc())

    def watchLastSeen(self):
        """
        Launches wLastSeen() in a new thread
        """
        threading.Thread(target=lambda self: self.wLastSeen(), args=([self])).start()

    def mainMenu(self):
        """
        Console - based main menu. Prints menu in console and handles user input.
        """
        answers = {
            'A': {'name': ('[A]uth ' + (
                '' if self.admin_apis[self.current_acc] is None else '(logged in: ' + self.admin_apis[
                    self.current_acc].login + ')')),
                  'foo': lambda: self.auth()},
            'F': {'name': '[F]ull load', 'foo': lambda: self.makeFullLoad()},
            'O': {'name': '[O]nline friends',
                  'foo': lambda: self.getOnline(self.getFileName('online'), int(input('depth:')))},
            'L': {'name': '[L]ast time online',
                  'foo': lambda: self.getFriendsInfo('', 'last_seen', int(input('depth:')),
                                                     self.getFileName('last_online'))},
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

    def load_groups(self, apis = None):
        f = open('groups.txt', 'r')
        for line in f:
            ids = line.split(sep='-')
            reg = ids[ids.__len__() - 1]
            ids.remove(reg)
            reg = reg.replace('\n', '')
            print(reg)
            for id in ids:
                if id and id.isdigit():
                    try:
                        loaded_users = self.getFromGroup(group_name=id, user_fields='last_seen', apis=apis)
                        counter  = 1
                        for loaded_users_chunk in loaded_users:
                            self.saveToFile(
                                obj=loaded_users_chunk,
                                name='RU-' + reg + '_' + id + '_' + str(counter))
                            counter += 1
                        loaded_users = None
                        loaded_users_chunk = None
                    except Exception as e:
                        print(e)

    def tkMenu(self):
        """
            Provides graphic interface
            """
        answers = {
            'A': {'name': ('Auth ' + (
                '' if self.admin_apis[self.current_acc] is None else '(logged in: ' + self.admin_apis[
                    self.current_acc].login + ')')),
                  'foo': lambda: auth_menu()},
            'FF': {'name': 'Full load', 'foo': lambda: loadConversationsMenu()},
            'F': {'name': 'Load conversations', 'foo': lambda: loadConversationsMenu()},
            'O': {'name': 'Online friends', 'foo': lambda: self.getOnline(self.getFileName('online'), 0)},
            'L': {'name': 'Last time online monitor (4 times/h 3h)', 'foo': lambda: self.watchLastSeen()},
            'G': {'name': 'Get from group', 'foo': lambda: group_chosen()},
            'GS': {'name': 'Load groups', 'foo': lambda: self.init_load_groups()},
            'LID': {'name': 'Load by id', 'foo': lambda: load_by_id()},
            'Q': {'name': 'Quit', 'foo': lambda: sys.exit()}
        }

        root = Tk()
        root.geometry("500x400")

        def loadMainMenu():
            """
                Loads and shows main menu
                """
            clear()
            for ans in answers.items():
                button = Button(bg='white', text=ans[1]['name'], command=lambda name=ans[0]: answers[name]['foo']())
                button.pack(fill=BOTH, expand=1)

        def clear():
            """
                Clears the scene - removes all the elements
                """
            for widget in root.winfo_children():
                widget.pack_forget()

        def group_chosen():
            """
                Loads and shows menu for choosing load from group properities
                """
            clear()
            Label(text="id or name:").pack()
            groupId = Entry(root)
            groupId.pack()
            Label(text="how many users").pack()
            quan = Entry(root)
            quan.pack()
            Label(text="fields (separate with comma, leave empty for all)").pack()
            Label(text="nickname, screen_name, sex, bdate, city, country, timezone, photo, has_mobile,\n"
                       "contacts, education, online, counters, relation, last_seen, activity,\n"
                       "can_write_private_message, can_see_all_posts, can_post, universities,\n"
                       "followers_count, counters, occupation").pack()
            user_fields = Entry(root)
            user_fields.pack()
            Label(text="folder prefix").pack()
            folder_prefix = Entry(root)
            folder_prefix.pack()
            button = Button(bg='white', text='Load', command=lambda: rep(1, lambda: self.saveToFile(
                self.getFromGroup(groupId.get(), int(quan.get()) if quan.get() else -1,
                                  user_fields=user_fields.get()), folder_prefix.get() + '_from_group')))
            button.pack(fill=BOTH, expand=1)
            button = Button(bg='white', text='To Menu', command=lambda: loadMainMenu())
            button.pack(fill=BOTH, expand=1)

        def rep(quan, foo):
            print(self.getTime())
            i = 0
            while (i < quan):
                print('repeating: ', i)
                print((self.getTime()))
                foo()
                i += 1
            print(self.getTime())

        def get_from_group_valid(id, quan, fields=''):
            group = self.admin_apis[self.current_acc].groups.getById(group_id=id, fields='members_count')
            time.sleep(self.SMALL_SLEEP_TIME)
            members_count = group[0]['members_count']
            users_need = round(quan)
            valid_users = {}
            offset = members_count - users_need
            while users_need > valid_users.__len__() and offset >= 0:
                last_users = self.getFromGroup(id, users_need - valid_users.__len__(), offset=offset)
                for user in last_users:
                    if not "deactivated" in user and not "is_closed" in user:
                        valid_users[user['id']] = user
                offset -= (users_need - valid_users.__len__())
            return valid_users

        def auth_menu():
            """
                Loads and shows auth menu
                """
            clear()
            Label(text="Tel:").pack()
            entryTel = Entry(root)
            entryTel.pack()
            Label(text="Pass:").pack()
            entryPas = Entry(root)
            entryPas.pack()
            button = Button(bg='white', text='Auth', command=lambda: loadMainMenu() if (
                    entryPas.get() and entryTel.get() and self.auth(tel=entryTel.get(),
                                                                    pas=entryPas.get())) else tkinter.messagebox.showinfo(
                "", "Failed to login"))
            button.pack(fill=BOTH, expand=1)

        def conversation_clicked(event):
            """
                Enables and disables conversations for further load
                :param event:
                :type event:
                """
            load = not self.tk_buttons[event]['load']
            self.tk_buttons[event]['load'] = load
            self.tk_buttons[event]['button'].config(bg='white' if load else 'red')
            if load:
                self.conversations_to_load.append(self.tk_buttons[event]['conversation'])
            else:
                self.conversations_to_load.remove(self.tk_buttons[event]['conversation'])

        def loadConversationsMenu():
            """
                Loads and shows available conversations to load
                """
            print("Loading converstions...")
            clear()
            Label(text="Red conversations wont be loaded").pack()
            if (len(self.tk_buttons) == 0):
                conversations = self.getConversations(20, 0)
            else:
                conversations = self.tk_buttons.items()

            Button(bg='white', text='Load!',
                   command=lambda: self.loadConversations(self.conversations_to_load)).pack(
                fill=BOTH, expand=1)
            Button(bg='white', text='Back', command=lambda: loadMainMenu()).pack(fill=BOTH, expand=1)
            Label(text="Conversations:").pack()
            if len(self.tk_buttons) == 0:
                for conversation in conversations:
                    time.sleep(0.3)
                    conversation_name = False
                    peer_id = conversation['conversation']['peer']['local_id']
                    if conversation['conversation']['peer']['type'] == 'user':
                        user = self.admin_apis[self.current_acc].users.get(
                            user_id=str(conversation['conversation']['peer']['id']))
                        conversation_name = user[0]['first_name'] + ' ' + user[0]['last_name']
                    else:
                        if ('chat_settings' in conversation['conversation']):
                            conversation_name = conversation['conversation']['chat_settings']['title']

                    if (conversation_name):
                        button = Button(bg='white', text=conversation_name,
                                        command=lambda name=conversation_name: conversation_clicked(name))
                        button.pack(fill=BOTH, expand=1)
                        self.tk_buttons.update(
                            {conversation_name: {'button': button, 'conversation': conversation, 'load': True}})
                        self.conversations_to_load.append(conversation)
            else:
                for conversation in conversations:
                    conversation[1]['button'].pack(fill=BOTH, expand=1)

        # auth_menu()
        loadMainMenu()
        root.mainloop()


VkLoader().tkMenu()
# makeFullLoad()
# auth()
# getOnline()
