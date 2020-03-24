import json
import bs4

filename0 = 'VK_Analyzer_2020-03-11_00-29-02/last_online_2020-03-11_00-36-21.txt'
filenames = ['VK_Analyzer_2020-02-12_17-22-42unis.txt', 'VK_Analyzer_2020-02-13_08-43-05unis.txt', 'VK_Analyzer_2020-02-13_10-16-54unis.txt',
             'VK_Analyzer_2020-02-13_19-22-25unis.txt', 'VK_Analyzer_2020-02-13_21-36-43unis.txt', 'VK_Analyzer_2020-02-13_22-20-21unis.txt', '456unis.txt']

a = json.load(open(filename0, 'r'))

for filename in filenames:
    b = json.load(open(filename, 'r'))
    for reg in a:
        if reg in b:
            if 'unis' in b[reg]:
                if 'unis' in a[reg]:
                        if len(a[reg]['unis']) < len(b[reg]['unis']):
                            print(' *'+reg + ' from ' + filename)
                            a[reg]['unis'] = b[reg]['unis']
                else:
                    print(reg + ' from '+filename)
                    a[reg]['unis'] = b[reg]['unis']
    print()
f = open('mergedRegions5.js', 'w')
f.write(bs4.BeautifulSoup(json.dumps(a)).prettify('unicode'))
f.close()