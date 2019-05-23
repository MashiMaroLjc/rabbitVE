#
# 剪辑视频
#


import cv2
import subprocess
import command
import time
import numpy as np
from lib import face_detection, face_compare
from util import *
import threading
from queue import Queue
import argparse
import os
from util import detect_face

# 图片队列,用于reader 和 worker的线程通信
image_q = Queue()
# 结果队列,用于主线程 和 worker的线程通信
result_q = Queue()


def get_reader(videoCapture, per_frame):
    def reader():
        frame_count = 0
        success, frame = videoCapture.read()
        while success:
            if (frame_count + 1) % per_frame == 0:
                image_q.put((frame, frame_count))
            frame_count += 1
            # print("Put {}/{} frame.... ".format(frame_count, total_frame_num))
            success, frame = videoCapture.read()
            if frame_count % 500 == 0:
                # 休息一下，防止worker相比读入图片处理太慢，导致太多图片堆积在队列中导致内存爆炸
                while not image_q.empty():
                    time.sleep(1)
        image_q.put((None, -1))

    return reader


def get_worker(model, compare_tool, max_v, total_frame_num, fps, no_strict, strict_threshold, debug):
    def worker():
        cut_index = []
        cur_index = [-1, -1]
        frame, frame_count = image_q.get()
        last_frame = None
        while frame_count > -1:
            print(">>> Deal {}/{} frame.... ".format(frame_count, total_frame_num))
            _, bboxes = detect_face(frame.copy(), model, max_v)
            # _, bboxes = model.detecte(frame)
            if len(bboxes) > 0:
                face_list = []
                for (top, right, bottom, left) in bboxes:
                    face_cut = frame[top:bottom, left:right]
                    face_list.append(face_cut)
                has_target_face, score = compare_tool.compare(face_list)
                if cur_index[0] == -1 and has_target_face:
                    print(">>> Find a target Face .... ")
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
                    if no_strict:
                        if last_frame is not None:
                            value = compareHist(last_frame, frame)
                            if value < strict_threshold:
                                if debug:
                                    cv2.imwrite("./test/hist/{}.png".format(frame_count),
                                                np.concatenate((last_frame, frame), axis=0))
                                cur_index[0] = int((frame_count - 2) / fps)  # 平滑
                                no_face = False
                    elif cur_index[0] != -1 and no_face:
                        cur_index[1] = int((frame_count + 2) / fps)  # 平滑
                        cut_index.append(cur_index.copy())
                        cur_index[0] = -1
                        cur_index[1] = -1  # finish a seg
            else:
                if cur_index[0] != -1:
                    cur_index[1] = int((frame_count + 2) / fps)
                    cut_index.append(cur_index.copy())
                    cur_index[0] = -1
                    cur_index[1] = -1  # finish a seg
            frame, frame_count = image_q.get()
        result_q.put(cut_index)

    return worker


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True,
                        help='video path')
    parser.add_argument('-t', '--target', type=str,
                        help='path of output cut video (default: ./output)', default="./output")
    parser.add_argument("-d", help="the detector type(default:cvdnn)", type=str, default="cvdnn",
                        choices=("cvdnn", "dlib_cnn", "dlib_hog"))
    parser.add_argument("-max_size", help="the max size of height or width of input image(defaule:1080)",
                        type=int, default=1280)

    parser.add_argument("-tf", help="threshold of detect the face", type=float, default=0.5)
    parser.add_argument("-ts", help="threshold of no strict method", type=float, default=0.3)
    parser.add_argument("-tcut", help="threshold of combine between two cutting results(second)", type=float,
                        default=10)

    parser.add_argument("--per_frame", help="the frequency of detect(frame)", type=int, default=10)
    parser.add_argument('--no_strict', help='use no strict method', action='store_true', default=False)
    parser.add_argument('--debug', help='Whether  debug', action='store_true', default=False)

    parser.add_argument("-smt", help="the similarity measure type(default:dlib)", type=str, default="dlib",
                        choices=("dlib",))
    parser.add_argument("--face_database", help="the path of face_database(default:./face)", type=str, default="./face")
    parser.add_argument("-tc", help="threshold of similarity measure(default:0.33)", type=float, default=0.33)
    parser.add_argument('--encode',
                        help='Whether encode the face from face database.if you do it before,you need not do it again.',
                        action='store_true', default=False)

    args = parser.parse_args()
    max_v = args.max_size
    out_dir = args.target
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    if args.debug and (not os.path.exists("./test/hist/")):
        os.makedirs("./test/hist/", exist_ok=True)
    if args.debug and (not os.path.exists("./test/target_face/")):
        os.makedirs("./test/target_face/", exist_ok=True)
    if args.d == "cvdnn":
        print(">>> Use CVDNN threshold.{}".format(args.tf))
        model = face_detection.FaceDetection(
            ('./model/deploy.prototxt', './model/res10_300x300_ssd_iter_140000_fp16.caffemodel'),
            conf_threshold=args.tf,
            model="cvdnn")
    else:
        print(">>> Use {} threshold.{}".format(args.d.upper(), args.tf))
        model = face_detection.FaceDetection(None, conf_threshold=args.tf,
                                             model=args.d)
    if args.smt == "dlib":
        encode_path = "./model/encode_result.pkl"
        if not os.path.exists(encode_path) or args.encode:
            encode_path = None
            print("# Encode the face ...")
        compare_tool = face_compare.FaceCompare(None, args.face_database,
                                                encode_path=encode_path,
                                                conf_threshold=args.tc)
    else:
        raise ValueError(">>> Not support the similarity measure type for now")
    videoCapture = cv2.VideoCapture(args.path)
    total_frame_num = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    print(">>> fps", fps)
    print(">>> use strict :{}".format(args.no_strict == False))
    t1 = threading.Thread(target=get_reader(videoCapture, args.per_frame))
    t1.start()
    t2 = threading.Thread(
        target=get_worker(model, compare_tool, max_v, total_frame_num, fps, args.no_strict, args.ts, args.debug))
    t2.start()
    t2.join()  # 主线程等待t2结束
    print(">>> Finish Deal.")
    cut_index = result_q.get()
    finall_index = []  # 合并cutindex

    for index in cut_index:
        if len(finall_index) == 0:
            finall_index.append(index)
        else:
            end = finall_index[-1][1]
            begin = index[0]
            if begin - end < args.tcut:
                finall_index[-1][1] = index[1]  # 合并
            else:
                finall_index.append(index)

    for i, index in enumerate(finall_index):
        begin, end = index
        begin = second_format(begin)
        end = second_format(end)
        if begin == -1:
            continue
        command_inp = command.video_cut.format(begin, end, args.path, "{}/cut_{}.mp4".format(out_dir, i))
        print(command_inp)
        process = subprocess.Popen(command_inp)
        process.wait()
    print(">>> Done.")    
