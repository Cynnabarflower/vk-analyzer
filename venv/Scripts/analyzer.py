import json
import pandas
import os
import matplotlib.pyplot as pyplot
import matplotlib.cm as cm
import datetime
from tkinter.filedialog import askopenfilename
import tempfile
from threading import Thread
import time
import random
import threading
import math
from Gui.Gui import *


# data_frame = pandas.read_csv('C:/Users/Dmitry/PycharmProjects/untitled/venv/Scripts/' + 'Onlineonline_map_sum2.csv')


def someFoo():
    for id in online_map:
        series = pandas.Series(online_map[id])
        series.name = str(id)
        data_frame = data_frame.append(series)
    for id in online_map:
        for el in online_map[id]:
            el['online'] = str(el['online'])
            el['scan'] = str(el['scan'])
    f = open(dirs[0] + 'online_map3.txt', 'w')
    json.dump(online_map, f)
    f.flush()
    f.close()
    data_frame.groupby(['city_name'])['id'].count().plot(kind='bar')
    pyplot.show()
    data_frame.groupby(['sex'])['id'].count().plot(kind='bar')
    pyplot.show()
    data_frame.groupby(['first_name'])['id'].count().plot(kind='bar')
    # data_frame['first_name'].plot()
    pyplot.show()
    # print(data_frame.to_string())
    print('done')


def getData(dir):
    if not dir.endswith('/'):
        dir += '/'
    conversationPath = dir + 'conversations/'
    usersPath = dir + 'users/'
    data_frame = pandas.DataFrame()
    data_frame['photos'] = None
    data_frame['posts'] = None
    data_frame['city_name'] = None

    if (True):
        if (os.path.exists(usersPath)):
            fileTree = os.walk(usersPath)
            for userFolders in fileTree:
                for userFolder in userFolders[1]:
                    userFolderName = userFolders[0] + userFolder
                    if os.path.exists(userFolderName + '/info.txt'):
                        userInfo = json.load(open(userFolderName + '/info.txt'))
                        series = pandas.Series(userInfo)
                        series.name = str(userInfo['id'])
                        data_frame = data_frame.append(series)
                        if 'city' in userInfo:
                            data_frame.at[str(userIЦnfo['id']), 'city_name'] = userInfo['city']['title']
                        if os.path.exists(userFolderName + '/info.txt'):
                            # userPhotos = json.load(open(userFolderName + '/photos.txt'))
                            data_frame.at[str(userInfo['id']), 'photos'] = 'userPhotos'
                        if (os.path.exists(userFolderName + '/posts.txt')):
                            # userPosts = json.load(open(userFolderName+'/posts.txt'))
                            data_frame.at[str(userInfo['id']), 'posts'] = 'userPosts'

            data_frame.groupby(['city_name'])['id'].count().plot(kind='bar')
            pyplot.show()
            data_frame.groupby(['sex'])['id'].count().plot(kind='bar')
            pyplot.show()
            data_frame.groupby(['first_name'])['id'].count().plot(kind='bar')
            # data_frame['first_name'].plot()
            pyplot.show()
            return

    words = dict()
    series = None
    if (os.path.exists(conversationPath)):
        conversationFiles = os.walk(conversationPath)
        for files in conversationFiles:
            for file in files[2]:
                obj = json.load(open(files[0] + file, 'r'))
                if (obj):
                    messages = obj[0]
                    for message in messages:
                        if 'text' in message and message['text']:
                            message_words = message['text'].split()
                            for word in message_words:
                                if len(word) < 3 or len(word) > 20:
                                    continue
                                word = word.lower()
                                while len(word) > 0 and not word[0].isalpha():
                                    word = word[1:]
                                while len(word) > 0 and not word[len(word) - 1].isalpha():
                                    word = word[:-1]
                                if not word:
                                    continue
                                if word in words:
                                    words[word] = words[word] + 1
                                else:
                                    words.update({word: 1})
        series = pandas.Series(words)
        series.name = 'count'
        df = pandas.DataFrame(series).sort_values('count', ascending=False)

        print(df.to_string())

        df[:40].plot(kind='bar')
        pyplot.show()


def getPlainTextFromMessages(dataFrame):
    return ''


def getSex(dir):
    data_frame = pandas.DataFrame()
    if not dir.endswith('/'):
        dir += '/'
    fileTree = os.walk(dir)
    fileTree.__next__()
    for onlineFolders in fileTree:
        for onlineFile in onlineFolders[2]:
            onlineData = json.load(open(fileName))
            loaded = 0
            for id in onlineData:
                loaded += 1
                if loaded % 1000:
                    print(loaded)
                    break
                series = pandas.Series(onlineData[id])
                series.name = str(id)
                data_frame = data_frame.append(series)

    data_frame.plot(kind='bar')
    pyplot.show()



app = Gui()
app.mainloop()

# getOnlineData('C:/Users/Dmitry/PycharmProjects/untitled/venv/Scripts/Online')
# getData('All messages 17.02/')
