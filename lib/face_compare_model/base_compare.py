class BaseCompare:

    def load_model(self, path):
        pass

    def preprocess(self,imgs):
        pass

    def compare(self, img1, img2):
        raise NotImplemented
