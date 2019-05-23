import tkinter as tk
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter import ttk
from tkinter import messagebox
from .gui_util import ExtractFaceView, VideoMergeView, PluginView, ClipView


class GUI:
    def __init__(self, config):
        self.config = config
        self.window = tk.Tk()
        self.widget_list = []
        self.extract_face_view_drawer = ExtractFaceView(self.window, self.config)
        self.video_merge_view_drawer = VideoMergeView(self.window, self.config)
        self.plugin_view_drawer = PluginView(self.window, self.config)
        self.clip_view_drawer = ClipView(self.window, self.config)
        self.initialize()

    def clean_view(self):
        for widget in self.widget_list:
            widget.destroy()
        self.widget_list = self.widget_list[:]

    def extract_view(self):
        self.clean_view()
        self.title_label["text"] = "FaceExtract"
        self.extract_face_view_drawer.draw(self.widget_list)

    def clip_view(self):
        self.title_label["text"] = "VideoClip"
        self.clean_view()
        self.clip_view_drawer.draw(self.widget_list)

    def merge_view(self):
        self.title_label["text"] = "VideoMerge"
        self.clean_view()
        self.video_merge_view_drawer.draw(self.widget_list)

    def frame_processor_view(self):
        self.title_label["text"] = "Frame Processor Plugins"
        self.clean_view()
        self.plugin_view_drawer.draw(self.widget_list)

    def initialize(self):
        self.window.title("RabbitVE")
        self.window.geometry(self.config["geometry"])
        self.window.resizable(width=False, height=False)
        self.title_label = tk.Label(self.window, text="RabbitVE", font=(None, 17))
        self.title_label.place(x=0, y=0)
        menu0 = tk.Menu(self.window)  # 参数是父级控件
        for x, func in zip(['Extract', 'Clip', 'Merge', 'ProcessorPlugins'],
                           [self.extract_view,
                            self.clip_view,
                            self.merge_view,
                            self.frame_processor_view]):
            menu0.add_command(label=x, command=func)  # 添加3个一级菜
        self.window['menu'] = menu0
        self.extract_view()

    def run(self):
        self.window.mainloop()
