import face_recognition
from .base_compare import BaseCompare
import numpy as np
import  cv2

class DLIBCOMPARE(BaseCompare):
    def __init__(self, conf_threshold=0.1):
        super(DLIBCOMPARE).__init__()
        self.img_encode_code = []
        self.conf_threshold = conf_threshold

    def preprocess(self, imgs):
        for img in imgs:
            if img is None:
                continue
            h, w, c = img.shape
            # img = cv2.resize(img, (64, 64))
            code = face_recognition.face_encodings(img, [(0, w, h, 0)])[0]
            self.img_encode_code.append(code)
            # self.img_encode_code_array = np.array(self.img_encode_code)

    def compare(self, img_list, img2=None):
        temp = []
        for img in img_list:
            h, w, c = img.shape
            # img = cv2.resize(img, (64, 64))
            code = face_recognition.face_encodings(img, [(0, w, h, 0)])
            if len(code) > 0:
                temp.append(code[0])
        res_list = []
        for temp_ in temp:
            res = face_recognition.compare_faces(self.img_encode_code, temp_, tolerance=self.conf_threshold)  # 越小越好
            res_list.append(res)
        return np.sum(res_list) > 0, res_list
