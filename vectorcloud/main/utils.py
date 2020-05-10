import os
from shutil import copy2, rmtree
import importlib
from git import Repo, cmd as git_cmd
from configparser import ConfigParser
from flask import render_template
from flask_socketio import emit
from vectorcloud import socketio, db
from vectorcloud.paths import (
    plugins_folder,
    plugins_js_folder,
    plugins_panels_folder,
    repositories_folder,
    sdk_config_file,
    root_folder,
)
from vectorcloud.main.models import Repositories, Vectors


# --------------------------------------------------------------------------------------
# UTILITY/MISC FUNCTIONS
# --------------------------------------------------------------------------------------
def trigger_reload():
    with open(os.path.join(root_folder, "reload_trigger.py"), "w") as file:
        file.write("reload_needed = True")
        file.close()


def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def database_init():
    # Initialize the Vectors table
    try:
        config = ConfigParser()
        config.read(sdk_config_file)
        for serial in config.sections():
            vector = Vectors.query.filter_by(serial=serial).first()
            if not vector:
                vector = Vectors()

            vector.serial = serial
            vector.cert_file = config.get(serial, "cert")
            vector.ip = config.get(serial, "ip")
            vector.name = config.get(serial, "name")
            vector.guid = config.get(serial, "guid")
            db.session.merge(vector)
            db.session.commit()

    except FileNotFoundError:
        pass

    # add official repo and install all plugins if no repo is configured
    if not Repositories.query.first():
        repo = add_repository(
            "https://github.com/rmountjoy92/VectorCloudOfficialPlugins",
            auto_update=True,
        )
        repositories = get_repositories(repo)
        for plugin in repositories[0].plugins:
            reinstall_plugin(plugin["name"], repo)

    # Reclone missing repositories
    for repository in Repositories.query.all():
        if not os.path.isdir(repository.fp):
            add_repository(
                repository.url, replace_existing=True, use_default_auto_update=True
            )

    # Auto-update repositories
    for repository in Repositories.query.filter_by(auto_update=True).all():
        update_repositories(repository)
        repositories = get_repositories(repository)
        for plugin in repositories[0].plugins:
            if f"{plugin['name']}.py" in os.listdir(plugins_folder):
                reinstall_plugin(plugin["name"], repository)


# --------------------------------------------------------------------------------------
# PLUGIN FUNCTIONS
# --------------------------------------------------------------------------------------
def add_repository(
    link, auto_update=False, replace_existing=False, use_default_auto_update=False
):
    name = link[link.rfind("/") + 1 :]
    path = os.path.join(repositories_folder, name.replace(".git", ""))
    Repo.clone_from(link, path)
    if replace_existing:
        repo = Repositories.query.filter_by(url=link).first()
        if use_default_auto_update:
            auto_update = repo.auto_update
    else:
        repo = Repositories()
    repo.url = link
    repo.name = name
    repo.fp = path
    repo.auto_update = auto_update
    db.session.add(repo)
    db.session.commit()
    return repo


def delete_repository(repo):
    rmtree(repo.fp)
    Repositories.query.filter_by(id=repo.id).delete()
    db.session.commit()


def get_repositories(repository=None):
    if not repository:
        repositories = Repositories.query.all()
    else:
        repositories = [repository]

    installed_plugins = os.listdir(plugins_folder)

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


def update_repositories(repo=None):
    if not repo:
        repos = Repositories.query.all()
    else:
        repos = [repo]
    for repo in repos:
        g = git_cmd.Git(repo.fp)
        g.pull()


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
    if interface_data.get("plugin_extra_html", None):
        for plugin_html in interface_data["plugin_extra_html"]:
            path = os.path.join(
                repositories_folder, repository.name, plugin_name, plugin_html
            )
            new_path = os.path.join(plugins_panels_folder, plugin_html)
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
    if f"{plugin_name}.py" not in os.listdir(plugins_folder):
        return f"No plugin named {plugin_name}"

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


def reinstall_plugin(plugin_name, repository=None):
    if not repository:
        repository = Repositories.query.first()
    uninstall_plugin(plugin_name, force=True)
    install_plugin(plugin_name, repository)


def start_plugins():
    if Vectors.query.first():
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
