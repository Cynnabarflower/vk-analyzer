import webbrowser
from tkinter import *

root = None

def mainMenu():
    root = Tk()
    root.geometry("500x400")
    for ans in answers.items():
        button = Button(bg='white', text=ans[1]['name'], command=lambda name=ans[0]: answers[name]['foo']())
        button.pack(fill=BOTH, expand=1)

f = open('site/map_values.js', 'w')

webbrowser.register('Chrome', None, webbrowser.BackgroundBrowser('C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'))
webbrowser.get('Chrome').open_new_tab(url = 'site/index.html')