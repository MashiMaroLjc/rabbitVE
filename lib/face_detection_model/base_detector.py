class BaseDetector:
    def load_model(self, path):
        raise NotImplemented

    def detection(self, img):
        raise NotImplemented
