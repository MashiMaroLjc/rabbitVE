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


class _ProcessView(tk.Toplevel):
    # 显示进度的子窗口
    def __init__(self, window, control_button, params, name):
        super(_ProcessView, self).__init__(window)
        self.title("RabbitVE FaceExtract")
        self.geometry("450x50")
        self.control_button = control_button
        self.control_button.config(state="disable")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.label = tk.Label(self, text="{}..".format(name))
        self.label.font = (None, 10)
        self.label.place(x=0, y=20)
        self.canvas_width = 270
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=16, bg="white")
        self.canvas.place(x=60, y=20)

        self.number_label = tk.Label(self, text="{}/{}".format(0, 0))
        self.number_label.font = (None, 10)
        self.number_label.place(x=330, y=20)

        ###
        self.params = params
        self.total_size = 0  # 进度条长度
        self.curr = 0  # 当前进度
        self.is_run = True  # 线程运行标志
        self.safe_exit = True
        self.threadings = []  # 方便管理
        self.threading_start()
        ####

    def _work(self):
        raise NotImplemented

    def work(self):
        self._work()
        self.exit()
        if self.safe_exit:
            messagebox.showinfo("Info", "Done.")
        else:
            messagebox.showwarning("Warning", "Not safe exit.")

    def change_ui(self):
        fill_line = self.canvas.create_rectangle(2, 2, 0, 2, width=0, fill="green")
        while self.is_run:
            if self.total_size < 1:
                continue  # 避免线程过早启动时，total size 为0
            self.number_label["text"] = "{}/{}".format(self.curr, int(self.total_size))
            n = int(self.curr / self.total_size * self.canvas_width)
            self.canvas.coords(fill_line, (0, 0, n, 30))
            # time.sleep(0.1)  # 不需要频繁修改UI

    def threading_start(self):
        worker = threading.Thread(target=self.work)
        worker.setDaemon(True)
        worker.start()
        changer = threading.Thread(target=self.change_ui)
        changer.setDaemon(True)
        changer.start()
        self.threadings.append(worker)
        self.threadings.append(changer)

    def exit(self):
        self.is_run = False
        time.sleep(0.1)
        self.control_button.config(state="normal")
        self.destroy()

    def on_closing(self):
        # 退出将结束线程
        self.safe_exit = False  # 手动退出不安全
        self.exit()
