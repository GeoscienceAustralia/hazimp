
import plugin_manager

def main():   
    # Load the plugins from the plugin directory.
    manager = plugin_manager.load_plugins()

    # Loop round the plugins and print their names.
    for plugin in manager.getAllPlugins():
        plugin.plugin_object.print_name()

if __name__ == "__main__":
    main()
