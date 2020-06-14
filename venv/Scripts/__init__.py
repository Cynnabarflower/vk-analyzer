import os
import sys
import configparser

work = os.path.abspath(os.path.join(os.path.join(os.path.abspath(__file__), os.pardir), os.pardir))
os.chdir(work)
sys.path.append(work + '\Lib')
sys.path.append(work + '\Data')
sys.path.append(work)

from Gui import *

app = Gui()
app.mainloop()
