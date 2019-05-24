class BasePlugin:
    def __init__(self):
        pass

    def initialize(self, params):
        self.params = params

    def transform(self, frame):
        raise NotImplemented

    def name(self):
        return "Plugin"

    def render_info(self):
        raise NotImplemented
