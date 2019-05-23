from .base_processor import BaseProcessor
from ..face_detection import FaceDetection
from ..face_compare import FaceCompare
import numpy as np
import cv2


class TargetFaceDetect(BaseProcessor):
    def __init__(self):
        super(TargetFaceDetect, self).__init__()

    def initialize(self, params):
        self.model = FaceDetection(params["path"], params["tf"], params["type"])
        self.compare_tool = FaceCompare(None, params["face_database"],
                                        encode_path=params["encode_path"],
                                        conf_threshold=params["tc"])

    def transform(self, frame):
        draw, bboxes = self.model.detecte(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        if len(bboxes) > 0:
            face_list = []
            for (top, right, bottom, left) in bboxes:
                face_cut = frame[top:bottom, left:right]
                face_list.append(face_cut)
            has_target_face, score = self.compare_tool.compare(face_list)
            if has_target_face:
                # print("# Find a target Face .... ")
                # bboxes = np.array(bboxes)
                for (top, right, bottom, left), s in zip(bboxes, score):
                    if np.sum(score) > 0:
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), int(720 / 150), 8)
        return cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)
