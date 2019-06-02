import tkinter as tk
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter import ttk

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
from .process_view import _ProcessView
from lib.align import aliner_instance


class ExtractFaceProcess(_ProcessView):
    # 显示进度的子窗口
    def __init__(self, window, control_button, params):
        super(ExtractFaceProcess, self).__init__(window, control_button, params, "Extract..")
        self.aligner = aliner_instance

    def _work(self):
        max_v = int(self.params['max_size'])
        out_dir = self.params['output']
        detector_type = self.params['detector_type']
        threshold = float(self.params["threshold"])
        video = self.params["video"]
        sort_type = self.params["sort_type"]
        if detector_type == "cvdnn":
            model = face_detection.FaceDetection(
                ('./model/deploy.prototxt', './model/res10_300x300_ssd_iter_140000_fp16.caffemodel'),
                conf_threshold=threshold,
                model="cvdnn")
        else:
            model = face_detection.FaceDetection(None, conf_threshold=threshold,
                                                 model=detector_type)
        img_ids = 0
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if video:
            for path in self.params["input"]:
                if not self.is_run:
                    break
                videoCapture = cv2.VideoCapture(path)
                total_frame_number = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
                self.total_size = total_frame_number
                success, frame = videoCapture.read()
                frame_count = 0
                while success and self.is_run:
                    frame_count += 1
                    self.curr = frame_count + 1
                    img, faces = detect_face(img, model, max_v)
                    if len(faces) < 1:
                        continue
                    for (top, right, bottom, left) in faces:
                        # img_cut = img[top:bottom, left:right]
                        face_cut = self.aligner.align(frame, [left, top, right, bottom])
                        new_path = os.path.join(out_dir, "{}.png".format(img_ids))
                        cv2.imwrite(new_path, face_cut)
                        img_ids += 1
                    success, frame = videoCapture.read()
        else:
            img_list = self.params["input"]
            self.total_size = len(img_list)
            for i, ip in enumerate(img_list):
                if not self.is_run:
                    break
                self.curr = i + 1
                img = cv2.imread(ip)
                img, faces = detect_face(img, model, max_v)
                if len(faces) < 1:
                    continue
                for (top, right, bottom, left) in faces:
                    img_cut = img[top:bottom, left:right]
                    new_path = os.path.join(out_dir, "{}.png".format(img_ids))
                    cv2.imwrite(new_path, img_cut)
                    img_ids += 1
        if sort_type == "hist":
            self.label["text"] = "Sort.."
            HistSort(out_dir, out_dir).sort()


class ExtractFaceView:
    def __init__(self, window, config):
        self.config = config
        self.window = window
        # self.processview.destroy()

    def openfile(self, event):
        if event.widget["text"] == "..":
            intput_type = self.input_type.get()
            if not intput_type:
                messagebox.showerror("Error", "please select the input type first.")
                return
            if intput_type == "video":
                self.input_filename = askopenfilenames(title='select', filetypes=[
                    ("all video format", ".mp4"),
                    ("all video format", ".flv"),
                    ("all video format", ".avi"),
                ])
            elif intput_type == "image":
                self.input_filename = askopenfilenames(title='select', filetypes=[
                    ("image", ".jpeg"),
                    ("image", ".png"),
                    ("image", ".jpg"),
                ])
            self.label0_["text"] = self.input_filename
        elif event.widget["text"] == "...":
            self.output_dir = askdirectory(title="select")
            self.label1_["text"] = self.output_dir

    def run_extract_face(self):
        if self.output_dir is None or self.input_filename is None:
            messagebox.showerror("Error", "please complete the params choice.")
            return
        params = {
            "input": self.input_filename,
            "output": self.output_dir,
            "video": self.input_type.get() == "video",
            "sort_type": self.sort_type.get(),
            "detector_type": self.detector_type.get(),
            "max_size": self.text2.get(),
            "threshold": self.text4.get()
        }
        ExtractFaceProcess(None, control_button=self.button, params=params)

    def draw(self, widget_list):
        label = tk.Label(self.window, text="InputType:")
        label.place(x=0, y=40)
        widget_list.append(label)

        self.input_type = tk.StringVar()
        checkbox = tk.Radiobutton(self.window, text="image", variable=self.input_type, value="image")
        checkbox.place(x=100, y=40)
        checkbox2 = tk.Radiobutton(self.window, text="video", variable=self.input_type, value="video")
        checkbox2.place(x=200, y=40)
        widget_list.append(checkbox)
        widget_list.append(checkbox2)

        self.input_filename = None
        label0 = tk.Label(self.window, text="Input :")
        label0.place(x=0, y=80)
        self.label0_ = tk.Label(self.window, text="", bg="white", width=50, height=1)
        self.label0_.place(x=60, y=80)
        button0_ = tk.Button(self.window, text="..", height=1, width=3)
        button0_.bind("<Button-1>", func=self.openfile)
        button0_.place(x=420, y=80)
        widget_list.append(label0)
        widget_list.append(self.label0_)
        widget_list.append(button0_)

        self.output_dir = None
        label1 = tk.Label(self.window, text="Output :")
        label1.place(x=0, y=120)
        self.label1_ = tk.Label(self.window, text="", bg="white", width=50, height=1)
        self.label1_.place(x=60, y=120)
        button1_ = tk.Button(self.window, text="...", height=1, width=3)
        button1_.bind("<Button-1>", func=self.openfile)
        button1_.place(x=420, y=120)
        widget_list.append(label1)
        widget_list.append(self.label1_)
        widget_list.append(button1_)

        label2 = tk.Label(self.window, text="Input MaxSize :")
        label2.place(x=0, y=160)
        self.text2 = tk.Entry(self.window)
        self.text2.place(x=100, y=160, height=20, width=50)
        self.text2.insert("end", self.config["max_size"])
        widget_list.append(label2)
        widget_list.append(self.text2)

        label3 = tk.Label(self.window, text="Detector :")
        label3.place(x=0, y=200)

        self.detector_type = tk.StringVar()
        detector_type_list = ttk.Combobox(self.window, width=12, textvariable=self.detector_type)
        detector_type_list['values'] = self.config["detector_type"]
        detector_type_list.current(0)  # default value index
        detector_type_list.place(x=100, y=200)
        widget_list.append(label3)
        widget_list.append(detector_type_list)

        label4 = tk.Label(self.window, text="Threshold( The bigger,the more stringent ):")
        label4.place(x=0, y=240)

        self.text4 = tk.Entry(self.window)
        self.text4.place(x=270, y=240, height=20, width=50)
        self.text4.insert("end", self.config["face_threshold"])

        widget_list.append(label4)
        widget_list.append(self.text4)

        label5 = tk.Label(self.window, text="Sort Type :")  # None or hist
        label5.place(x=0, y=280)
        self.sort_type = tk.StringVar()
        sort_type_list = ttk.Combobox(self.window, width=12, textvariable=self.sort_type)
        sort_type_list['values'] = self.config["sort_type"]
        sort_type_list.current(0)  # default value index
        sort_type_list.place(x=100, y=280)
        widget_list.append(label5)
        widget_list.append(sort_type_list)

        self.button = tk.Button(self.window, text="Run", command=self.run_extract_face)
        # button.bind("<Button-1>", func=run_extract_face)  # 1 左键 2 中 3 右
        self.button.place(x=420, y=320, width=200)
        widget_list.append(self.button)

        for widget in widget_list:
            if isinstance(widget, tk.Label):
                widget.font = (None, 10)
