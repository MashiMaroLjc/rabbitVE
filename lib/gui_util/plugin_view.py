import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from tkinter import ttk
from ..plugin_loder import PluginLoader
from ..plugin.BasePlugin import BasePlugin
from .process_view import _ProcessView
from ..plugin import param_type
from tkinter import messagebox
import os
import command
import cv2
import subprocess


class PluginProcessView(_ProcessView):
    # 显示进度的子窗口
    def __init__(self, window, control_button, params, name):
        super(PluginProcessView, self).__init__(window, control_button, params, name)
        self.plugin = self.params["plugin"]
        self.curr = 0

    def transform(self, frame):
        self.curr += 1
        if not self.is_run:
            return
        return self.plugin.transform(frame)

    def _work(self):
        if not os.path.exists("./UserData/temp"):
            os.makedirs("./UserData/temp")

        inp = self.params["input"]
        out = self.params["output"]
        frame_count = 0
        videoCapture = cv2.VideoCapture(inp)
        total_frame_num = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = videoCapture.get(cv2.CAP_PROP_FPS)
        success, frame = videoCapture.read()
        self.total_size = total_frame_num
        self.label["text"] = "Deal.."
        while success and self.is_run:
            frame_count += 1
            self.curr = frame_count
            frame = self.plugin.transform(frame)
            cv2.imwrite("./UserData/temp/{}.png".format(frame_count), frame)
            success, frame = videoCapture.read()
        self.label["text"] = "Video.."
        cmd = command.imgs2video.format("./UserData/temp/%d.png", fps, "./UserData/temp/temp_video.mp4")
        s = subprocess.Popen(cmd)
        s.wait()
        self.label["text"] = "Audio.."
        cmd = command.extract_audio.format(inp, "./UserData/temp/temp.mp3")
        s = subprocess.Popen(cmd)
        s.wait()
        self.label["text"] = "Syn..."
        cmd = command.video_audio_combine.format("./UserData/temp/temp_video.mp4", "./UserData/temp/temp.mp3", out)
        s = subprocess.Popen(cmd)
        s.wait()
        os.remove("./UserData/temp/temp_video.mp4")
        os.remove("./UserData/temp/temp.mp3")
        for x in os.scandir("./UserData/temp/"):
            if x.path.endswith(".png"):
                os.remove(x.path)

    def on_closing(self):
        self.is_run = False
        if os.path.exists("./UserData/temp/temp_video.mp4"):
            os.remove("./UserData/temp/temp_video.mp4")
        if os.path.exists("./UserData/temp/temp.mp3"):
            os.remove("./UserData/temp/temp.mp3")
        for x in os.scandir("./UserData/temp/"):
            if x.path.endswith(".png"):
                os.remove(x.path)
        super(PluginProcessView, self).on_closing()


class PluginParmaView(tk.Toplevel):
    def __init__(self, window, render_info, geometry, plugin: BasePlugin, input_path, output_path):
        super(PluginParmaView, self).__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.window = window
        self.plugin = plugin
        self.geometry(geometry)
        self.resizable(width=False, height=False)
        self.title_label = tk.Label(self, text="RabbitVE - {}".format(plugin.name()), font=(None, 17))
        self.title_label.place(x=0, y=0)
        self.register_params = dict()
        self.y_ = 0
        self._render(render_info)

    def collect_params(self):
        params = {}
        for k, v in self.register_params.items():
            if isinstance(v[0], tk.Entry):
                value = v[0].get()
                if v[1] == param_type.INT:
                    value = int(value)
                elif v[1] == param_type.FLOAT:
                    value = float(value)
                params[k] = value
            elif isinstance(v[0], tk.IntVar):
                value = v[0].get()
                if v[1] == param_type.BOOLEAN:
                    value = (value == 1)
                params[k] = value
        return params

    def run(self):

        param = self.collect_params()
        self.plugin.initialize(param)
        process_param = {
            "input": self.input_path,
            "output": self.output_path,
            "plugin": self.plugin
        }
        PluginProcessView(self, self.button, process_param, "Deal")

    def render_number(self, info):
        y = (len(self.register_params) + 1) * 40
        self.y_ = y + 40
        name = info["name"]
        label = tk.Label(self, text=name.replace("_", " ") + " :", font=(None, 10))
        label.place(x=0, y=y)
        text = tk.Entry(self)
        x = len(name) * 10
        text.place(x=x, y=y, height=20, width=50)
        default = info.get("default", None)
        self.register_params[name] = (text, info["type"])
        if default:
            text.insert("end", str(default))

    def render_boolearn(self, info):
        y = (len(self.register_params) + 1) * 40
        self.y_ = y + 40
        name = info["name"]
        label = tk.Label(self, text=name.replace("_", " ") + " :", font=(None, 10))
        label.place(x=0, y=y)

        check = tk.IntVar()
        check_button = tk.Checkbutton(self, text="{} ?".format(name),
                                      variable=check, onvalue=1, offvalue=0,
                                      height=4, width=10, font=(None, 10))
        x = len(name) * 10
        check_button.place(x=x, y=y - 20)
        if info["default"]:
            check.set(1)
        else:
            check.set(0)
        self.register_params[name] = (check, info["type"])

    def _render(self, render_info):
        for info in render_info:
            type_ = info["type"]
            if type_ == param_type.INT or type_ == param_type.FLOAT:
                self.render_number(info)
            if type_ == param_type.BOOLEAN:
                self.render_boolearn(info)
        self.button = tk.Button(self, text="Run", command=self.run)
        # button.bind("<Button-1>", func=run_extract_face)  # 1 左键 2 中 3 右
        self.button.place(x=420, y=self.y_ + 40, width=200)




class PluginView:
    def __init__(self, window, config):
        self.config = config
        self.window = window

    def openfile(self, event):
        if event.widget["text"] == "..":
            self.input_filename = askopenfilename(title='select', filetypes=[
                ("all video format", ".mp4"),
                ("all video format", ".flv"),
                ("all video format", ".avi"),
            ])
            self.label0_["text"] = self.input_filename
        elif event.widget["text"] == "...":
            self.save_file = asksaveasfilename(title="save", filetypes=[
                ("all video format", ".mp4"),
                ("all video format", ".flv"),
                ("all video format", ".avi"),
            ], initialfile="result.mp4")
            self.label1_["text"] = self.save_file

    def load_plugin(self):
        if self.input_filename is None or self.save_file is None:
            messagebox.showerror("Error", "please complete the params choice.")
            return
        plugin_name = self.plugin_type.get()
        plugin = PluginLoader(plugin_name).plugin
        render_info = plugin.render_info()
        if isinstance(render_info, tk.Toplevel):
            render_info(self.window)
        else:
            PluginParmaView(self.window, render_info, self.config["geometry"], plugin,
                            self.input_filename, self.save_file)

    def draw(self, widget_list):
        self.input_filename = None
        label0 = tk.Label(self.window, text="Video :")
        label0.place(x=0, y=40)
        self.label0_ = tk.Label(self.window, text="", bg="white", width=50, height=1)
        self.label0_.place(x=100, y=40)
        button0_ = tk.Button(self.window, text="..", height=1, width=3)
        button0_.bind("<Button-1>", func=self.openfile)
        button0_.place(x=460, y=40)
        widget_list.append(label0)
        widget_list.append(self.label0_)
        widget_list.append(button0_)

        self.save_file = None
        label1 = tk.Label(self.window, text="Output :")
        label1.place(x=0, y=80)
        self.label1_ = tk.Label(self.window, text="", bg="white", width=50, height=1)
        self.label1_.place(x=100, y=80)
        button1_ = tk.Button(self.window, text="...", height=1, width=3)
        button1_.bind("<Button-1>", func=self.openfile)
        button1_.place(x=460, y=80)
        widget_list.append(label1)
        widget_list.append(self.label1_)
        widget_list.append(button1_)

        label3 = tk.Label(self.window, text="Plugin :")
        label3.place(x=0, y=120)
        self.plugin_type = tk.StringVar()
        plugin_type_list = ttk.Combobox(self.window, width=20, textvariable=self.plugin_type)
        plugin_type_list['values'] = list(self.config["plugin_list"])
        plugin_type_list.current(0)  # default value index
        plugin_type_list.place(x=100, y=120)
        widget_list.append(label3)
        widget_list.append(plugin_type_list)

        self.button = tk.Button(self.window, text="Load", command=self.load_plugin)
        # button.bind("<Button-1>", func=run_extract_face)  # 1 左键 2 中 3 右
        self.button.place(x=420, y=160, width=200)
        widget_list.append(self.button)
