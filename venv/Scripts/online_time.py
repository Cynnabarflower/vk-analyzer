import pandas as pd
import numpy as np
import json
import moustache_graph
import tkinter as tk
import time
import os

def foo(save_dir, addedFiles):
    users = pd.DataFrame(None, columns=['id'])
    counter = 0
    save_name = addedFiles[0].split('/')[-2]
    for addedFile in addedFiles:
        try:
            js_packs = json.load(open(addedFile, 'r'))
            total = js_packs.__len__() + 1
            df = pd.DataFrame(js_packs)[['id', 'scan_time', 'last_seen']]
            df = df.dropna()
            df['last_seen_from_mn'] = df['last_seen'].apply(lambda x: time.gmtime(x.get('time')))
            df['last_seen_from_mn'] = df['last_seen_from_mn'].apply(
                lambda x: (x.tm_hour * 60 + x.tm_min) * 60 + x.tm_sec).astype(int)
            users = users.merge(df[['id', 'last_seen_from_mn']], on='id', how='outer', suffixes=('', counter))
        except Exception as e:
            print(e)
            print(addedFile)
        counter += 1
        print(counter, addedFile.split('/')[-1])
        if counter % 30 == 0 and not users.empty:
            users = users.transform(lambda x: sorted(x, key=pd.isnull), 1).dropna(how='all', axis=1)
    if not users.empty:
        if counter % 30 != 0:
            users = users.transform(lambda x: sorted(x, key=pd.isnull), 1).dropna(how='all', axis=1)
        users.id = users.id.astype(int)

        users.to_csv(save_dir + '/' + save_name + '.csv', index=False, header=False, chunksize=100000)


dir_name = tk.filedialog.askdirectory()
save_dir = tk.filedialog.askdirectory()
paths = next(os.walk('.'))[1]
for path in paths:
    if 'VK' in path:
        added_files = []
        for subpath, subdir, files in os.walk(dir_name + '/' + path):
            for name in files:
                if not 'last_seen' in name:
                    added_files.append(os.path.join(subpath, name))
                    if added_files.__len__() > 3:
                        break
        if added_files.__len__() > 0:
            try:
                foo(save_dir, added_files)
            except Exception as e:
                print(e)
                print(added_files)
