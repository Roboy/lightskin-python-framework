#!/usr/bin/python3

import time
from datetime import datetime
import requests
import importlib, types
import queue
import signal
from threading import Thread
import os, sys, traceback

import tkinter as tk

from LightSkin import *
from LightSkinViz import *


window = tk.Tk()
window.title('Light Skin Simulation')
window.minsize(400, 300)



window.mainloop()

# Main program logic follows:
#if __name__ == '__main__':
#
