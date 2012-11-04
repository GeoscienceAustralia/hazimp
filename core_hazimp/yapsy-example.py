from yapsy.PluginManager import PluginManager

def main():   
    # Load the plugins from the plugin directory.
    manager = PluginManager()
    manager.setPluginPlaces(["plugins"])
    manager.collectPlugins()

    # Loop round the plugins and print their names.
    for plugin in manager.getAllPlugins():
        plugin.plugin_object.print_name()

if __name__ == "__main__":
    main()
