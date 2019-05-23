import tkinter as tk
from tkinter.filedialog import askopenfilenames, askdirectory, asksaveasfilename
from tkinter import ttk
from tkinter import messagebox
import cv2
import os
from .process_view import _ProcessView
import glob
import re
import command
import subprocess


class VideoMergeProcess(_ProcessView):
    # 显示进度的子窗口
    def __init__(self, window, control_button, params,name):
        super(VideoMergeProcess, self).__init__(window, control_button, params,name)

    def get_sort_key(self, pattern, format, common_prefix):
        prog = re.compile(pattern)

        def sort_key(s):
            sub = prog.search(s)[0]
            sub = sub.replace(format, "").replace(common_prefix, "")
            return int(sub)

        return sort_key

    def _work(self):
        format = self.params["f"]
        common_prefix = self.params["common_prefix"]
        output = self.params["output"]
        dir_ = self.params["dir"]
        pattern = "cut_[0-9]{1,}\%s" % (format)
        temp_file = "video.txt"
        self.label["text"] = "Scan.."
        input_path = os.path.join(dir_, common_prefix + "*{}".format(format))
        video_list = glob.glob(input_path)
        video_list = sorted(video_list, key=self.get_sort_key(pattern, format, common_prefix))
        temp = open(temp_file, "w")
        self.total_size = len(video_list)
        for i, video_name in enumerate(video_list):
            temp.write("file \'{}\'\n".format(video_name))
            self.curr = i + 1
        temp.close()
        cmd = command.video_merge.format(temp_file, output)
        self.label["text"] = "Merge.."
        process = subprocess.Popen(cmd)
        process.wait()
        os.remove(temp_file)


class VideoMergeView:
    def __init__(self, window, config):
        self.config = config
        self.window = window

    def openfile(self, event):
        if event.widget["text"] == "...":
            self.video_dir = askdirectory(title="select")
            self.label0_["text"] = self.video_dir

        if event.widget["text"] == "..":
            self.save_file = asksaveasfilename(title="save", filetypes=[
                ("all video format", ".mp4"),
                ("all video format", ".flv"),
                ("all video format", ".avi"),
            ], initialfile="result.mp4")
            self.label1_["text"] = self.save_file

    def run_video_merge(self):

        if self.video_dir is None or self.save_file is None:
            messagebox.showerror("Error", "please complete the params choice.")
            return
        params = {
            "f": self.format.get(),
            "common_prefix": self.common_prefix.get(),
            "output": self.save_file,
            "dir": self.video_dir
        }
        VideoMergeProcess(self.window, self.button, params,"")

    def draw(self, widget_list):

        self.video_dir = None
        label0 = tk.Label(self.window, text="Video Dir:")
        label0.place(x=0, y=40)
        self.label0_ = tk.Label(self.window, text="", bg="white", width=50, height=1)
        self.label0_.place(x=70, y=40)
        button1_ = tk.Button(self.window, text="...", height=1, width=3)
        button1_.bind("<Button-1>", func=self.openfile)
        button1_.place(x=420, y=40)
        widget_list.append(label0)
        widget_list.append(self.label0_)
        widget_list.append(button1_)

        self.save_file = None
        label1 = tk.Label(self.window, text="Output :")
        label1.place(x=0, y=80)
        self.label1_ = tk.Label(self.window, text="", bg="white", width=50, height=1)
        self.label1_.place(x=70, y=80)
        button1_ = tk.Button(self.window, text="..", height=1, width=3)
        button1_.bind("<Button-1>", func=self.openfile)
        button1_.place(x=420, y=80)
        widget_list.append(label1)
        widget_list.append(self.label1_)
        widget_list.append(button1_)

        label2 = tk.Label(self.window, text="Common Prefix:")
        label2.place(x=0, y=120)
        self.common_prefix = tk.Entry(self.window)
        self.common_prefix.insert("end", "cut_")
        self.common_prefix.place(x=110, y=120, height=20, width=50)
        widget_list.append(label2)
        widget_list.append(self.common_prefix)

        label3 = tk.Label(self.window, text="Format :")
        label3.place(x=0, y=160)

        self.format = tk.StringVar()
        format_type_list = ttk.Combobox(self.window, width=12, textvariable=self.format)
        format_type_list['values'] = (".mp4", ".flv", ".avi")
        format_type_list.current(0)  # default value index
        format_type_list.place(x=100, y=160)
        widget_list.append(label3)
        widget_list.append(format_type_list)

        self.button = tk.Button(self.window, text="Run", command=self.run_video_merge)
        # button.bind("<Button-1>", func=run_extract_face)  # 1 左键 2 中 3 右
        self.button.place(x=420, y=200, width=200)
        widget_list.append(self.button)

        for widget in widget_list:
            if isinstance(widget, tk.Label):
                widget.font = (None, 10)
