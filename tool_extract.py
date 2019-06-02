import argparse
import os

import cv2

from lib import face_detection
from lib.util import detect_face
from lib.align import cvdnn as align_cvdnn

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True,
                        help='path of image or video need to sort.if image,you need to enter the image dir.'
                             'if video you need to enter the full name of video.')
    parser.add_argument('-t', '--target', type=str,
                        help='path of output face (default: ./face)', default="./face")
    parser.add_argument('-v', '--video', help='Whether  video', action='store_true', default=False)
    parser.add_argument("-d", help="the detector type(default:cvdnn)", type=str, default="cvdnn",
                        choices=("cvdnn", "dlib_cnn", "dlib_hog"))
    parser.add_argument("-tf", help="threshold of detect the face", type=float, default=0.5)
    parser.add_argument("-max_size", help="the max size of height or width of input image(defaule:1080)",
                        type=int, default=1080)
    parser.add_argument("-align", help="alignment", choices=("cvdnn","none"),
                        type=str, default="cvdnn")
    args = parser.parse_args()

    max_v = args.max_size
    out_dir = args.target
    if args.d == "cvdnn":
        print("Use CVDNN threshold.{}".format(args.tf))
        model = face_detection.FaceDetection(
            ('./model/deploy.prototxt', './model/res10_300x300_ssd_iter_140000_fp16.caffemodel'),
            conf_threshold=args.tf,
            model="cvdnn")
    else:
        print("Use {} threshold.{}".format(args.d, args.tf))
        model = face_detection.FaceDetection(None, conf_threshold=args.tf,
                                             model=args.d)
    if args.align == "cvdnn":
        aligner = align_cvdnn.CVDNN()
    else:
        aligner = None
    img_ids = 0
    if not os.path.exists(args.target):
        os.makedirs(args.target)
    if args.video:
        videoCapture = cv2.VideoCapture(args.path)
        total_frame_number = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
        success, img = videoCapture.read()
        frame_count = 0
        while success:
            frame_count += 1
            img, faces = detect_face(img, model, max_v)
            if len(faces) < 1:
                continue
            for (top, right, bottom, left) in faces:
                if aligner is not None:
                    img_cut = aligner.align(img,[left, top, right, bottom])
                else:
                    img_cut = img[top:bottom, left:right]
                    img_cut = cv2.resize(img_cut, (128, 128))
                new_path = os.path.join(out_dir, "{}.png".format(img_ids))
                cv2.imwrite(new_path, img_cut)
                img_ids += 1
            print("Done {}/{}".format(frame_count, total_frame_number))
            success, frame = videoCapture.read()
    else:
        img_list = [x.path for x in os.scandir(args.path) if
                    x.path.endswith("jpg") or x.path.endswith("png") or x.path.endswith("jpeg")]
        for ip in img_list:
            img = cv2.imread(ip)
            img, faces = detect_face(img, model, max_v)
            if len(faces) < 1:
                print("Image {} can't find a face".format(ip))
                continue
            for (top, right, bottom, left) in faces:
                if aligner is not None:
                    img_cut = aligner.align(img,[left, top, right, bottom])
                else:
                    # print((top, right, bottom, left))
                    img_cut = img[top:bottom, left:right]
                    # print(img_cut.shape)
                    img_cut = cv2.resize(img_cut, (128, 128))
                new_path = os.path.join(out_dir, "{}.png".format(img_ids))
                print("Image save in {}".format(new_path))
                cv2.imwrite(new_path, img_cut)
                img_ids += 1
