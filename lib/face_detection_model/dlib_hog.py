from .base_detector import BaseDetector
import dlib
import cv2
import face_recognition


class DLIBHOG(BaseDetector):
    def __init__(self, conf_threshold):
        super(DLIBHOG, self).__init__()
        self.conf_threshold = conf_threshold

    def load_model(self, path):
        pass

    def detection(self, frame):
        bboxes = []
        frameDraw = frame.copy()
        frameHeight = frameDraw.shape[0]
        faces = face_recognition.face_locations(frame, number_of_times_to_upsample=0, model="hog") #top, right, bottom, left
        for (top, right, bottom, left) in faces:
            cv2.rectangle(frameDraw, (left, top), (right, bottom), (0, 255, 0), int(frameHeight / 150), 8)
            bboxes.append([top, right, bottom, left])
        return frameDraw, bboxes
