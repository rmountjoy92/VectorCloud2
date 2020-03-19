import os
import glob
from secrets import token_hex
from htmlmin.main import minify
from flask import (
    render_template,
    url_for,
    redirect,
    request,
    Blueprint,
    jsonify,
)
from flask_login import current_user
from vectorcloud.main.models import Files, Vectors, Repositories
from vectorcloud.main.utils import (
    run_plugin,
    get_repositories,
    get_plugins,
    uninstall_plugin,
    install_plugin,
)
from vectorcloud.paths import cache_folder
from vectorcloud import app, db


main = Blueprint("main", __name__)


# ------------------------------------------------------------------------------
# intial routes and functions (before/after request)
# ------------------------------------------------------------------------------
@app.after_request
def response_minify(response):
    """
    minify html response to decrease site traffic
    """
    if response.content_type == "text/html; charset=utf-8":
        response.set_data(minify(response.get_data(as_text=True)))

        return response
    return response


# blocks access to all pages (except public routes) unless the user is
# signed in.
@main.before_app_request
def check_valid_login():

    if "/api/" in request.path:
        return
    elif current_user.is_authenticated:
        return
    elif getattr(app.view_functions[request.endpoint], "is_public", False):
        return
    elif request.endpoint.startswith("static"):
        return

    else:
        return redirect(url_for("user_system.login"))


# ------------------------------------------------------------------------------
# /home
# ------------------------------------------------------------------------------
@main.route("/")
@main.route("/home", methods=["GET", "POST"])
def home():
    vectors = Vectors.query.all()

    repositories = get_repositories()

    plugins, plugin_icons, plugin_panels, plugins_js = get_plugins()

    return render_template(
        "main/home.html",
        vectors=vectors,
        plugins=plugins,
        plugin_icons=plugin_icons,
        plugin_panels=plugin_panels,
        plugins_js=plugins_js,
        repositories=repositories,
    )


@main.route("/run", methods=["POST"])
def run():
    options = {}
    for fieldname, value in request.form.items():
        if fieldname != "plugin_name" and len(value) >= 1:
            options[fieldname] = value
    return run_plugin(request.form.get("plugin_name"), options)


@main.route("/delete_plugin", methods=["GET"])
def delete_plugin():
    output = uninstall_plugin(request.args.get("plugin_name"))
    if output == "success":
        return "success"
    else:
        return output


@main.route("/install_plugin_from_repo", methods=["GET"])
def install_plugin_from_repo():
    repository = Repositories.query.filter_by(id=request.args.get("repo_id")).first()
    output = install_plugin(request.args.get("plugin_name"), repository)
    if output == "success":
        return "success"
    else:
        return output


# ------------------------------------------------------------------------------
# TCDROP routes
# ------------------------------------------------------------------------------
@main.route("/tcdrop/cacheFile", methods=["POST"])
def cacheFile():
    f = request.files.get("file")
    ext = f.filename.split(".")[1]
    random_hex = token_hex(16)
    fn = f"{random_hex}.{ext}"
    path = os.path.join(cache_folder, fn)
    f.save(path)
    html = render_template(
        "main/tcdrop-file-row.html", orig_fn=f.filename, fn=fn, id=random_hex
    )
    file = Files(name=f.filename, path=path, cache=fn, folder="cache")
    db.session.add(file)
    db.session.commit()
    return jsonify(data={"cached": fn, "html": html})


@main.route("/tcdrop/clearCache", methods=["GET"])
def clearCache():
    files = glob.glob(cache_folder + "/*")
    for file in files:
        if ".no" not in file:
            os.remove(file)
    Files.query.filter_by(folder="cache").delete()
    db.session.commit()
    return "success"


@main.route("/tcdrop/deleteCachedFile", methods=["GET"])
def deleteCachedFile():
    f = request.args.get("file")
    path = os.path.join(cache_folder, f)
    Files.query.filter_by(path=path).delete()
    db.session.commit()
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return "success"


# @main.route("/tcdrop/addLocalFile", methods=["GET"])
# def addLocalFile():
#     f = request.args.get("file")
#     email_cache = request.args.get("email_cache")
#     ext = f.split(".")[1]
#     random_hex = token_hex(16)
#     fn = f"{random_hex}.{ext}"
#     if email_cache == "true":
#         file = Files.query.filter_by(cache=f).first()
#         orig_fn = file.name
#         old_path = os.path.join(email_cache_folder, f)
#     else:
#         old_path = os.path.join(pdf_folder, f)
#         orig_fn = f
#     path = os.path.join(cache_folder, fn)
#     copyfile(old_path, path)
#     html = render_template(
#         "main/tcdrop-file-row.html", orig_fn=orig_fn, fn=fn, id=random_hex
#     )
#     file = Files(name=orig_fn, path=path, cache=fn, folder="cache")
#     db.session.add(file)
#     db.session.commit()
#     return jsonify(data={"file": fn, "html": html})
