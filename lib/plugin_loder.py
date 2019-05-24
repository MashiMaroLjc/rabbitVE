class PluginLoader:

    def __init__(self, plugin_name):
        m = __import__("lib.plugin.{}".format(plugin_name), fromlist=(plugin_name,))
        obj = getattr(m, plugin_name)
        self.plugin = obj()





