class BaseProcessor:
    def __init__(self):
        pass

    def initialize(self, params):
        self.params = params

    def transform(self, frame):
        raise NotImplemented
