from lib.gui import GUI
from lib.util import load_config

if __name__ == "__main__":
    config = load_config("./config.yaml")
    GUI(config).run()
