import json
import pandas
import os
import matplotlib.pyplot as pyplot

def getData(dir):
    if not dir.endswith('/'):
        dir += '/'
    conversationPath = dir + 'conversations/'
    usersPath = dir + 'users/'
    data_frame = pandas.DataFrame()
    data_frame['photos'] = None
    data_frame['posts'] = None
    data_frame['city_name'] = None

    if (False):
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
                           data_frame.at[str(userInfo['id']), 'city_name'] = userInfo['city']['title']
                        if os.path.exists(userFolderName + '/info.txt'):
                            #userPhotos = json.load(open(userFolderName + '/photos.txt'))
                            data_frame.at[str(userInfo['id']), 'photos'] = 'userPhotos'
                        if (os.path.exists(userFolderName+'/posts.txt')):
                            #userPosts = json.load(open(userFolderName+'/posts.txt'))
                            data_frame.at[str(userInfo['id']), 'posts'] = 'userPosts'
            print(data_frame.to_string())
            data_frame.groupby(['city_name'])['id'].count().plot(kind='bar')
            pyplot.show()
            data_frame.groupby(['sex'])['id'].count().plot(kind='bar')
            pyplot.show()
            data_frame.groupby(['first_name'])['id'].count().plot(kind='bar')
           # data_frame['first_name'].plot()
            pyplot.show()


    words = dict()
    series = None
    if (os.path.exists(conversationPath)):
        conversationFiles = os.walk(conversationPath)
        for files in conversationFiles:
            for file in files[2]:
                obj = json.load(open(files[0]+file, 'r'))
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
                                while len(word) > 0 and not word[len(word)-1].isalpha():
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


getData('All messages 17.02/')

