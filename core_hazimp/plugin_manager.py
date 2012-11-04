from yapsy.PluginManager import PluginManager

def load_plugins():   
    """ Load the plugins from the plugin directory.
    """

    manager = PluginManager()
    manager.setPluginPlaces(["plugins"])
    manager.collectPlugins()
    
    return manager


if __name__ == "__main__":
    pass
