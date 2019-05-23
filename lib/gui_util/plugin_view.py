import tkinter as tk
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter import ttk
from tkinter import messagebox
import threading
import time
from ..util import detect_face, HistSort
from .. import face_detection
import cv2
import os


class PluginView:
    def __init__(self, window, config):
        self.config = config
        self.window = window

    def draw(self, widget_list):
        label = tk.Label(self.window, text="Coming soon ......")
        label.place(x=0, y=40)
        widget_list.append(label)
