import os
import sys
import configparser

work = r"C:\Users\Dmitry\PycharmProjects\vk-analyzer\venv"
os.chdir(work)
sys.path.append(work + '\Lib')
sys.path.append(work + '\Data')
sys.path.append(work)

from Gui import *

app = Gui()
app.mainloop()
