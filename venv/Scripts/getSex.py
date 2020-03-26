import json
import pandas
import os
import matplotlib.pyplot as pyplot
import datetime


def getSex(dir):
    data_frame = pandas.DataFrame()
    fileName = dir
    onlineData = json.load(open(fileName))
    loaded = 0
    for loaf in onlineData:
        for user in loaf:
            loaded += 1
            if loaded % 1000 == 0:
                print(loaded)
                #break
            series = pandas.Series({'sex' : 'M' if user['sex'] == 1 else 'F'})
            series.name = str(id)
            data_frame = data_frame.append(series)
    data_frame = data_frame.groupby(['sex']).size()
    data_frame.plot()
    pyplot.show()
    data_frame.plot(kind='bar')
    pyplot.show()
    data_frame.plot(kind='barh')
    pyplot.show()
    data_frame.plot(kind='hist')
    pyplot.show()
    data_frame.plot(kind='box')
    pyplot.show()
    data_frame.plot(kind='pie')
    pyplot.show()

getSex('C:/Users/Dmitry/PycharmProjects/untitled/venv/Scripts/Pikabu/from_group_2020-03-17_23-02-23.txt')
