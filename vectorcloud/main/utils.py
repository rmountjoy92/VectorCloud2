import os
from shutil import copy2
import importlib
from git import Repo
from flask import render_template
from flask_socketio import emit
from vectorcloud import socketio, db
from vectorcloud.paths import (
    plugins_folder,
    plugins_js_folder,
    plugins_panels_folder,
    repositories_folder,
)
from vectorcloud.main.models import Repositories

# --------------------------------------------------------------------------------------
# UTILITY/MISC FUNCTIONS
# --------------------------------------------------------------------------------------


def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def database_init():
    pass


# --------------------------------------------------------------------------------------
# PLUGIN FUNCTIONS
# --------------------------------------------------------------------------------------
def add_repository(link):
    name = link[link.rfind("/") + 1 :]
    path = os.path.join(repositories_folder, name)
    Repo.clone_from(link, path)
    repo = Repositories()
    repo.url = link
    repo.name = name
    repo.fp = path
    db.session.add(repo)
    db.session.commit()


def get_repositories():
    installed_plugins = os.listdir(plugins_folder)
    repositories = Repositories.query.all()
    for repository in repositories:
        repository.plugins = []
        for subdir in os.listdir(repository.fp):
            if "." not in subdir:
                spec = importlib.util.spec_from_file_location(
                    f"{subdir}",
                    os.path.join(repository.fp, f"{subdir}", f"{subdir}.py"),
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                plugin = module.Plugin()
                interface_data = plugin.interface_data()
                if f"{subdir}.py" in installed_plugins:
                    installed = True
                else:
                    installed = False
                repository.plugins.append(
                    {
                        "name": subdir,
                        "description": interface_data["plugin_description"],
                        "installed": installed,
                    }
                )
    return repositories


def get_plugins():
    plugins = []
    plugin_icons = []
    plugin_panels = ""
    plugins_js = []
    plugin_files = os.listdir(plugins_folder)
    plugin_files = sorted(plugin_files)
    for plugin_file in plugin_files:
        name, extension = os.path.splitext(plugin_file)
        if extension.lower() == ".py" and name not in ["utils", "__init__"]:
            interface_data = get_plugin_interface_data(name)
            plugins.append(
                {
                    "name": name,
                    "description": interface_data.get("plugin_description", None),
                    "options": interface_data.get("plugin_settings", None),
                    "icons": interface_data.get("plugin_icons", None),
                    "panels": interface_data.get("plugin_panels", None),
                    "js": interface_data.get("plugin_js", None),
                    "dependencies": interface_data.get("plugin_dependencies", None),
                }
            )
            plugin_icons.append(interface_data.get("plugin_icons", None))
            plugins_js.append(interface_data.get("plugin_js", None))
            panels = interface_data.get("plugin_panels", None)
            if panels:
                for panel in panels:
                    plugin_panels += render_template(
                        f"plugins/{panel['template']}", panel=panel
                    )
    return plugins, plugin_icons, plugin_panels, plugins_js


def remove_repository():
    pass


def install_plugin(plugin_name, repository=None):
    if f"{plugin_name}.py" in os.listdir(plugins_folder):
        return "There is already a plugin with that name installed. Aborting."
    if not repository:
        repository = Repositories.query.first()
    plugin_path = os.path.join(
        repositories_folder, repository.name, plugin_name, plugin_name + ".py"
    )
    new_plugin_path = os.path.join(plugins_folder, plugin_name + ".py")
    copy2(plugin_path, new_plugin_path)
    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plugin = module.Plugin()
    interface_data = plugin.interface_data()
    if interface_data.get("plugin_panels", None):
        for plugin_panel in interface_data["plugin_panels"]:
            path = os.path.join(
                repositories_folder,
                repository.name,
                plugin_name,
                plugin_panel["template"],
            )
            new_path = os.path.join(plugins_panels_folder, plugin_panel["template"])
            copy2(path, new_path)
    if interface_data.get("plugin_js", None):
        for plugin_js in interface_data["plugin_js"]:
            path = os.path.join(
                repositories_folder, repository.name, plugin_name, plugin_js
            )
            new_path = os.path.join(plugins_js_folder, plugin_js)
            copy2(path, new_path)

    if hasattr(plugin, "on_install"):
        plugin.on_install()

    return "success"


def check_plugin_dependencies(plugin_name):
    plugin_files = os.listdir(plugins_folder)
    dependencies = []
    for plugin_file in plugin_files:
        name, extension = os.path.splitext(plugin_file)
        if extension.lower() == ".py" and name not in ["__init__"]:
            interface_data = get_plugin_interface_data(name)
            if interface_data.get("plugin_dependencies", None):
                dependencies += interface_data.get("plugin_dependencies", None)
    if plugin_name in dependencies:
        return False
    else:
        return True


def uninstall_plugin(plugin_name, force=False):
    if check_plugin_dependencies(plugin_name) is True or force is True:
        plugin_path = os.path.join(plugins_folder, plugin_name + ".py")
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        plugin = module.Plugin()
        interface_data = plugin.interface_data()
        if interface_data.get("plugin_panels", None):
            for plugin_panel in interface_data["plugin_panels"]:
                path = os.path.join(plugins_panels_folder, plugin_panel["template"])
                os.remove(path)
        if interface_data.get("plugin_js", None):
            for plugin_js in interface_data["plugin_js"]:
                path = os.path.join(plugins_js_folder, plugin_js)
                os.remove(path)

        if hasattr(plugin, "on_uninstall"):
            plugin.on_uninstall()

        os.remove(plugin_path)
        return "success"
    else:
        return "There is another plugin that depends on this one. Uninstall cancelled."


def start_plugins():
    plugin_files = os.listdir(plugins_folder)
    plugin_files = sorted(plugin_files)
    for plugin_file in plugin_files:
        name, extension = os.path.splitext(plugin_file)
        if extension.lower() == ".py" and name not in ["utils", "__init__"]:
            module = importlib.import_module(f"vectorcloud.plugins.{name}", ".")
            plugin = module.Plugin(name)
            if hasattr(plugin, "on_startup"):
                plugin.on_startup()


def run_plugin(plugin_name, options={}):
    vector_id = options.get("vector_id", "")
    emit("vector_busy", vector_id, broadcast=True, namespace="/")
    try:
        module = importlib.import_module(f"vectorcloud.plugins.{plugin_name}", ".")
    except ImportError:
        module = importlib.import_module(
            f"vectorcloud.custom_plugins.{plugin_name}", "."
        )

    plugin = module.Plugin(plugin_name, **options)
    output = plugin.run()
    emit("vector_free", vector_id, broadcast=True, namespace="/")
    return output


@socketio.on("run_plugin")
def handle_run_plugin(json):
    options = {}
    for key, value in json.items():
        if key != "name":
            options[key] = value

    run_plugin(json["name"], options)


def get_plugin_interface_data(plugin_name):
    module = importlib.import_module(f"vectorcloud.plugins.{plugin_name}", ".")
    plugin = module.Plugin(plugin_name)
    return plugin.interface_data()
