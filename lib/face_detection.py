from .face_detection_model import detector_dict


class FaceDetection:
    def __init__(self, path, conf_threshold=0.5,model='cvdnn'):
        if model not in ["dlib_cnn", "dlib_hog", "cvdnn"]:
            raise ValueError("Not support model for now")

        self.model = detector_dict[model](conf_threshold)
        self.model.load_model(path)

    def detecte(self, img):
        return self.model.detection(img)

