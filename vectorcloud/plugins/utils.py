import importlib


def run_plugin(plugin_name, options={}):
    try:
        module = importlib.import_module(f"vectorcloud.plugins.{plugin_name}", ".")
    except ImportError:
        module = importlib.import_module(
            f"vectorcloud.custom_plugins.{plugin_name}", "."
        )

    plugin = module.Plugin(plugin_name, **options)
    return plugin.run()


def get_plugin_options(plugin_name):
    module = importlib.import_module(f"vectorcloud.plugins.{plugin_name}", ".")
    plugin = module.Plugin(plugin_name)
    return plugin.plugin_settings


def get_plugin_description(plugin_name):
    module = importlib.import_module(f"vectorcloud.plugins.{plugin_name}", ".")
    plugin = module.Plugin(plugin_name)
    return plugin.plugin_description


def install_dependancies(plugin_name):
    pass


def send_server_message():
    pass


def prompt_ui():
    pass
