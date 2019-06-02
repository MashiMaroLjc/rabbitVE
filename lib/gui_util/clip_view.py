import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import ttk
from tkinter import messagebox
import threading
import numpy as np
import time
from ..util import detect_face, HistSort, second_format, calc_continue_func_dict
from .. import face_detection, face_compare
import cv2
import command
import subprocess
import os
from queue import Queue
from .process_view import _ProcessView
from lib.align import aliner_instance


class ClipProcess(_ProcessView):
    # 显示进度的子窗口
    def __init__(self, window, control_button, params):
        super(ClipProcess, self).__init__(window, control_button, params, "")
        self.cut_index = []
        self.image_queue = Queue()
        self.aligner = aliner_instance

    def get_reader(self, videoCapture, per_frame):
        def reader():
            frame_count = 0
            success, frame = videoCapture.read()
            while success and self.is_run:
                if (frame_count + 1) % per_frame == 0:
                    self.image_queue.put((frame, frame_count))
                frame_count += 1
                # print("Put {}/{} frame.... ".format(frame_count, total_frame_num))
                success, frame = videoCapture.read()
                if frame_count % 500 == 0:
                    # 休息一下，防止worker相比读入图片处理太慢，导致太多图片堆积在队列中导致内存爆炸
                    while not self.image_queue.empty():
                        time.sleep(1)
            self.image_queue.put((None, -1))

        return reader

    def get_worker(self, model, compare_tool, max_v, total_frame_num, fps, continue_type, strict_threshold, debug):
        def worker():
            cur_index = [-1, -1]
            frame, frame_count = self.image_queue.get()
            last_frame = None
            self.total_size = total_frame_num
            while frame_count > -1 and self.is_run:
                self.curr = frame_count + 1
                _, bboxes = detect_face(frame.copy(), model, max_v)
                # _, bboxes = model.detecte(frame)
                if len(bboxes) > 0:
                    face_list = []
                    for (top, right, bottom, left) in bboxes:
                        # face_cut = frame[top:bottom, left:right]
                        face_cut = self.aligner.align(frame, [left, top, right, bottom])
                        face_list.append(face_cut)
                    has_target_face, score = compare_tool.compare(face_list)
                    if cur_index[0] == -1 and has_target_face:
                        print("# Find a target Face .... ")
                        if debug:
                            bboxes = np.array(bboxes)
                            for (top, right, bottom, left), s in zip(bboxes, score):
                                if np.sum(score) > 0:
                                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), int(720 / 150), 8)
                                cv2.imwrite("./test/target_face/{}.png".format(frame_count), frame)
                        cur_index[0] = int((frame_count - 2) / fps)  # 平滑
                        last_frame = frame.copy()
                    elif not has_target_face:
                        no_face = True
                        if continue_type != "none":
                            if last_frame is not None:
                                value = calc_continue_func_dict[continue_type](last_frame, frame)
                                if value < strict_threshold:
                                    if debug:
                                        cv2.imwrite("./test/hist/{}.png".format(frame_count),
                                                    np.concatenate((last_frame, frame), axis=0))
                                    cur_index[0] = int((frame_count - 2) / fps)  # 平滑
                                    no_face = False
                        elif cur_index[0] != -1 and no_face:
                            cur_index[1] = int((frame_count + 2) / fps)  # 平滑
                            self.cut_index.append(cur_index.copy())
                            cur_index[0] = -1
                            cur_index[1] = -1  # finish a seg
                else:
                    if cur_index[0] != -1:
                        cur_index[1] = int((frame_count + 2) / fps)
                        self.cut_index.append(cur_index.copy())
                        cur_index[0] = -1
                        cur_index[1] = -1  # finish a seg
                frame, frame_count = self.image_queue.get()

        return worker

    def _work(self):
        self.label["text"] = "Clip..."
        input_path = self.params["input"]
        max_v = int(self.params['max_size'])
        out_dir = self.params['output']
        detector_type = self.params['detector_type']
        face_threshold = float(self.params["face_threshold"])
        smt = self.params["smiliar_measure_method"]
        encode = self.params["learn"]
        face_database = self.params["face_database"]
        fst = float(self.params["face_similar_threshold"])
        shear_frequency = int(self.params["shear_frequency"])
        strict_threshold = float(self.params["retain_frame_check_threshold"])
        continue_type = self.params["retain_frame_check"]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        if detector_type == "cvdnn":
            model = face_detection.FaceDetection(
                ('./model/deploy.prototxt', './model/res10_300x300_ssd_iter_140000_fp16.caffemodel'),
                conf_threshold=face_threshold,
                model="cvdnn")
        else:
            model = face_detection.FaceDetection(None, conf_threshold=face_threshold,
                                                 model=detector_type)
        if smt == "dlib":
            encode_path = "./model/encode_result.pkl"
            if not os.path.exists(encode_path) or encode:
                encode_path = None
            compare_tool = face_compare.FaceCompare(None, face_database,
                                                    save_path="./model/encode_result.pkl",
                                                    encode_path=encode_path,
                                                    conf_threshold=fst, gui=self)
        else:
            raise ValueError(">>> Not support the similarity measure type for now")
        videoCapture = cv2.VideoCapture(input_path)
        total_frame_num = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = videoCapture.get(cv2.CAP_PROP_FPS)
        t1 = threading.Thread(target=self.get_reader(videoCapture, shear_frequency))
        t1.setDaemon(True)
        t1.start()
        t2 = threading.Thread(
            target=self.get_worker(model, compare_tool, max_v, total_frame_num, fps, continue_type
                                   , strict_threshold, False))
        t2.setDaemon(True)
        t2.start()
        t2.join()  # 主线程等待t2结束
        cut_index = self.cut_index
        if not self.is_run:
            return
        finall_index = []  # 合并cutindex

        for index in cut_index:
            if len(finall_index) == 0:
                finall_index.append(index)
            else:
                end = finall_index[-1][1]
                begin = index[0]
                if begin - end < 10:
                    finall_index[-1][1] = index[1]  # 合并
                else:
                    finall_index.append(index)
        self.label["text"] = "Write..."
        for i, index in enumerate(finall_index):
            begin, end = index
            begin = second_format(begin)
            end = second_format(end)
            if begin == -1:
                continue
            command_inp = command.video_cut.format(begin, end, input_path, "{}/cut_{}.mp4".format(out_dir, i))
            process = subprocess.Popen(command_inp)
            process.wait()


class ClipView:
    def __init__(self, window, config):
        self.config = config
        self.window = window
        # self.processview.destroy()

    def openfile(self, event):
        if event.widget["text"] == "..":
            self.input_filename = askopenfilename(title='select', filetypes=[
                ("all video format", ".mp4"),
                ("all video format", ".flv"),
                ("all video format", ".avi"),
            ])

            self.label0_["text"] = self.input_filename
        elif event.widget["text"] == "...":
            self.output_dir = askdirectory(title="select")
            self.label1_["text"] = self.output_dir
        elif event.widget["text"] == "....":
            self.face_dir = askdirectory(title="select")
            self.label_face_["text"] = self.face_dir

    def run_video_clip(self):
        if self.output_dir is None or self.input_filename is None:
            messagebox.showerror("Error", "please complete the params choice.")
            return
        params = {
            "input": self.input_filename,
            "output": self.output_dir,
            "detector_type": self.detector_type.get(),
            "max_size": self.text2.get(),
            "face_threshold": self.text4.get(),
            "face_similar_threshold": self.text5.get(),
            "face_database": self.face_dir,
            "learn": (self.check_learn.get() == 1),
            "shear_frequency": self.text6.get(),
            "smiliar_measure_method": self.smiliar_measure_method.get(),
            "retain_frame_check_threshold": self.text6_.get(),
            "retain_frame_check": self.retain_frame_check.get()
        }
        ClipProcess(None, control_button=self.button, params=params)

    def draw(self, widget_list):

        self.check_learn = tk.IntVar()
        check_button = tk.Checkbutton(self.window, text="learn ?", variable=self.check_learn, onvalue=1, offvalue=0,
                                      height=4, width=10, font=(None, 10))
        check_button.place(x=490, y=110)
        widget_list.append(check_button)

        self.input_filename = None
        label0 = tk.Label(self.window, text="Input :")
        label0.place(x=0, y=40)
        self.label0_ = tk.Label(self.window, text="", bg="white", width=50, height=1)
        self.label0_.place(x=100, y=40)
        button0_ = tk.Button(self.window, text="..", height=1, width=3)
        button0_.bind("<Button-1>", func=self.openfile)
        button0_.place(x=460, y=40)
        widget_list.append(label0)
        widget_list.append(self.label0_)
        widget_list.append(button0_)

        self.output_dir = None
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

        self.face_dir = None
        label_face = tk.Label(self.window, text="Face Database :")
        label_face.place(x=0, y=120)
        self.label_face_ = tk.Label(self.window, text="", bg="white", width=50, height=1)
        self.label_face_.place(x=100, y=120)
        button1_ = tk.Button(self.window, text="....", height=1, width=3)
        button1_.bind("<Button-1>", func=self.openfile)
        button1_.place(x=460, y=120)
        widget_list.append(label_face)
        widget_list.append(self.label_face_)
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

        label4 = tk.Label(self.window, text="Face Threshold( The bigger,the more stringent ):")
        label4.place(x=0, y=240)
        self.text4 = tk.Entry(self.window)
        self.text4.place(x=340, y=240, height=20, width=50)
        self.text4.insert("end", self.config["face_threshold"])
        widget_list.append(label4)
        widget_list.append(self.text4)

        label5 = tk.Label(self.window, text="Face Similar Threshold( The smaller,the more stringent ):")
        label5.place(x=0, y=280)
        self.text5 = tk.Entry(self.window)
        self.text5.place(x=340, y=280, height=20, width=50)
        self.text5.insert("end", self.config["face_similar_threshold"])
        widget_list.append(label5)
        widget_list.append(self.text5)

        label6 = tk.Label(self.window, text="Shear Frequency(frame) :")
        label6.place(x=0, y=320)
        self.text6 = tk.Entry(self.window)
        self.text6.place(x=180, y=320, height=20, width=50)
        self.text6.insert("end", self.config["shear_frequency"])
        widget_list.append(label6)
        widget_list.append(self.text6)
        #
        label7 = tk.Label(self.window, text="Retain Frame check :")
        label7.place(x=0, y=360)
        self.retain_frame_check = tk.StringVar()
        retain_frame_check_list = ttk.Combobox(self.window, width=12, textvariable=self.retain_frame_check)
        retain_frame_check_list['values'] = self.config["retain_frame_check"]
        retain_frame_check_list.current(0)  # default value index
        retain_frame_check_list.place(x=180, y=360)
        widget_list.append(label7)
        widget_list.append(retain_frame_check_list)

        label6_ = tk.Label(self.window, text="Retain Frame check threshold ( The smaller,the more stringent ) :")
        label6_.place(x=0, y=400)
        self.text6_ = tk.Entry(self.window)
        self.text6_.place(x=400, y=400, height=20, width=50)
        self.text6_.insert("end", self.config["retain_frame_check_threshold"])
        widget_list.append(label6_)
        widget_list.append(self.text6_)

        label8 = tk.Label(self.window, text="Smiliar Measure Method:")
        label8.place(x=0, y=440)
        self.smiliar_measure_method = tk.StringVar()
        smiliar_measure_method_list = ttk.Combobox(self.window, width=12, textvariable=self.smiliar_measure_method)
        smiliar_measure_method_list['values'] = self.config["smiliar_measure_method"]
        smiliar_measure_method_list.current(0)  # default value index
        smiliar_measure_method_list.place(x=180, y=440)
        widget_list.append(label8)
        widget_list.append(smiliar_measure_method_list)

        self.button = tk.Button(self.window, text="Run", command=self.run_video_clip)
        # button.bind("<Button-1>", func=run_extract_face)  # 1 左键 2 中 3 右
        self.button.place(x=420, y=480, width=200)
        widget_list.append(self.button)

        for widget in widget_list:
            if isinstance(widget, tk.Label):
                widget.font = (None, 10)
