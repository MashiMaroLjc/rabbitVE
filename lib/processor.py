from .processor_plugin import processor_dict


class Processor:
    def __init__(self, process_name):
        self.process = processor_dict[process_name]()

    def initialize(self, params):
        self.process.initialize(params)

    def transform(self, frame):
        return self.process.transform(frame)
