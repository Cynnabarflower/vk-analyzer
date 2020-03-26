import json
import pandas
import os
import matplotlib.pyplot as pyplot
import datetime


def get_sex(dir):
    data_frame = pandas.DataFrame()
    file_name = dir
    online_data = json.load(open(file_name))
    loaded = 0
    for loaf in online_data:
        for user in loaf:
            loaded += 1
            if loaded % 1000 == 0:
                print(loaded)

            series = pandas.Series({'sex': 'M' if user['sex'] == 1 else 'F'})
            series.name = str(id)
            data_frame = data_frame.append(series)
    data_frame = data_frame.groupby(['sex']).size()
    data_frame.plot()
    pyplot.show()
    data_frame.plot(kind='bar')
    pyplot.show()

    data_frame.plot(kind='pie')
    pyplot.show()


def get_online_data(*dirs):
    data_frame = pandas.DataFrame()
    online_map = dict()
    for dir in dirs:
        if not dir.endswith('/'):
            dir += '/'
        file_tree = os.walk(dir)
        file_tree.__next__()
        for onlineFolders in file_tree:
            for onlineFile in onlineFolders[2]:
                file_time = datetime.datetime.strptime(onlineFile[len('last_online_')::][:-4], '%Y-%m-%d_%H-%M-%S')
                file_name = onlineFolders[0] + '/' + onlineFile
                print(file_name)
                online_data = json.load(open(file_name))
                loaded = 0
                for id in online_data:
                    loaded += 1
                    if loaded > 5000:
                        break
                    if not 'last_seen' in online_data[id]:
                        continue
                    online_data[id]['last_seen']['time'] = datetime.datetime.fromtimestamp(
                        online_data[id]['last_seen']['time'])
                    if 'scan_time' in online_data[id]:
                        online_data[id]['last_seen']['scan_time'] = datetime.datetime.fromtimestamp(
                            online_data[id]['scan_time'])
                    else:
                        online_data[id]['last_seen']['scan_time'] = file_time

                    if id in online_map:
                        online_map[id] += [{'online': online_data[id]['last_seen']['time'],
                                            'scan': online_data[id]['last_seen']['scan_time'],
                                            'now': online_data[id]['online']
                                            }]
                    else:
                        if 'last_seen' in online_data[id]:
                            online_map[id] = [{'online': online_data[id]['last_seen']['time'],
                                               'scan': online_data[id]['last_seen']['scan_time'],
                                               'now': online_data[id]['online']
                                               }]
        break

    print('loading complete')
    formated_map = dict()
    progress = 0
    print(len(online_map), ' users')
    for id in online_map:
        progress += 1
        if progress % 1000 == 0:
            print(progress)
        quaters = dict()
        for online_time in online_map[id]:
            quaters[online_time['scan'].time()] = online_time['now']
        formated_map[id] = quaters
        series = pandas.Series(formated_map[id])
        series.name = str(id)
        data_frame = data_frame.append(series)
    data_frame.to_csv(dirs[0] + 'online_map.csv')
    data_frame = data_frame.sum(axis=0)
    data_frame.to_csv(dirs[0] + 'online_map_sum2.csv')
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


get_sex('C:/Users/Dmitry/PycharmProjects/untitled/venv/Scripts/Pikabu/from_group_2020-03-17_23-02-23.txt')
get_online_data('C:/Users/Dmitry/PycharmProjects/untitled/venv/Scripts/Online')

