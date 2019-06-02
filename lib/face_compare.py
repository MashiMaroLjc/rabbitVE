from .face_compare_model import compare_dict
import cv2
import os
import pickle
import scipy
import face_recognition


class FaceCompare:
    def __init__(self, path, known_img_path, save_path,encode_path=None, conf_threshold=0.5, model='dlib', gui=None):
        if model not in ["dlib"]:
            raise ValueError("Not support model for now")
        self.model = compare_dict[model](conf_threshold)
        self.model.load_model(path)
        img_list = []
        if encode_path is None:
            img_path = [x.path for x in os.scandir(known_img_path) if
                        x.path.endswith("jpg") or x.path.endswith("png") or x.path.endswith("jpeg")]
            for i, p in enumerate(img_path):
                if gui is None:
                    print("preprocess img ", p)
                else:
                    gui.label["text"] = "Encode..."
                    gui.curr = i + 1
                    gui.total_size = len(img_path)
                img = cv2.imread(p)
                img_list.append(img)
            self.model.preprocess(img_list)
            print("image encode result save in {}".format(save_path))
            pickle.dump(self.model.img_encode_code, open(save_path, "wb"))
        else:
            obj = pickle.load(open(encode_path, "rb"))
            self.model.img_encode_code = obj
            print("{} encode".format(len(obj)))


    def compare(self, img):
        return self.model.compare(img)
