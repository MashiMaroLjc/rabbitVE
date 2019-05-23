from .base_detector import BaseDetector

import cv2


class CVDNN(BaseDetector):
    def __init__(self, conf_threshold):
        super(CVDNN, self).__init__()
        self.conf_threshold = conf_threshold

    def load_model(self, path):
        proto, caffemodel = path
        self.net = cv2.dnn.readNetFromCaffe(proto, caffemodel)

    def detection(self, frame):
        #### https: // blog.csdn.net / github_39611196 / article / details / 85307457
        frameOpenCVDnn = frame.copy()
        frameHeight = frameOpenCVDnn.shape[0]
        frameWidth = frameOpenCVDnn.shape[1]
        blob = cv2.dnn.blobFromImage(frameOpenCVDnn, 1.0, (300, 300), [104, 117, 123], False, False)

        self.net.setInput(blob)
        detections = self.net.forward()
        bboxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                bboxes.append([y1, x2, y2, x1])
                cv2.rectangle(frameOpenCVDnn, (x1, y1), (x2, y2), (0, 255, 0), int(frameHeight / 150), 8)
                # cv2.rectangle(frameDraw, (left, top), (right, bottom), (0, 255, 0), int(frameHeight / 150), 8)
                # bboxes.append([top, right, bottom, left])
                ### 横向是x，纵向是y

        return frameOpenCVDnn, bboxes
