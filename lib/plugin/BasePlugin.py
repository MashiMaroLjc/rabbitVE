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
        """
                #  list item(dict) 的key（可选） name type option default
                :return: a class extend tk.Toplevel  or list
        """
        raise NotImplemented
