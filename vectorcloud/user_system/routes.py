import subprocess
import os
from flask import render_template, url_for, redirect, Blueprint, jsonify, request
from flask_login import login_user, logout_user
from vectorcloud.user_system.forms import LoginForm, RegisterForm, VectorForm
from vectorcloud.user_system.models import User
from vectorcloud.user_system.utils import add_user_func
from vectorcloud import bcrypt
from vectorcloud.main.utils import public_route, trigger_reload
from vectorcloud.main.models import Vectors
from vectorcloud.user_system.authenticate_vector import main as authenticate_vector
from vectorcloud.paths import vc_folder

user_system = Blueprint("user_system", __name__)


# ------------------------------------------------------------------------------
# User system routes
# ------------------------------------------------------------------------------
# onboarding
@public_route
@user_system.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    user = User.query.first()
    vector = Vectors.query.first()
    register_form = RegisterForm()
    vector_form = VectorForm()
    return render_template(
        "user/onboarding.html",
        title="Onboarding",
        register_form=register_form,
        vector_form=vector_form,
        user=user,
        vector=vector,
    )


# login page
@public_route
@user_system.route("/login", methods=["GET", "POST"])
def login():
    if not User.query.first() or not Vectors.query.first():
        return redirect(url_for("user_system.onboarding"))
    form = LoginForm()
    return render_template("user/login.html", title="Login", form=form)


@public_route
@user_system.route("/check_login", methods=["POST"])
def check_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if not user:
            response = {"err": "User not found"}

        elif bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            response = {"url": url_for("main.home")}
        else:
            response = {"err": "Password is wrong"}
    else:
        response = {"err": str(form.errors)}

    return jsonify(data=response)


# this logs the user out and redirects to the login page
@user_system.route("/logout")
def logout():

    logout_user()
    return redirect(url_for("user_system.login"))


@public_route
@user_system.route("/welcome")
def welcome():
    register_form = RegisterForm()
    return render_template(
        "user/welcome.html", title="Welcome", register_form=register_form
    )


@public_route
@user_system.route("/add_user", methods=["POST"])
def add_user():
    form = RegisterForm()
    if form.validate_on_submit():
        user = add_user_func(request.form.get("username"), request.form.get("password"))
        login_user(user)
        return jsonify(data={"err": "success", "url": url_for("main.home")})
    else:
        return jsonify(data={"err": str(form.errors)})


@public_route
@user_system.route("/add_vector", methods=["POST"])
def add_vector():
    anki_email = request.form.get("anki_email")
    anki_password = request.form.get("anki_password")
    ip = request.form.get("ip")
    name = request.form.get("name")
    serial = request.form.get("serial")
    cmd = f'python3 -m vectorcloud.user_system.anki_configure -e "{anki_email}" -p "{anki_password}" -i "{ip}" -n "{name}" -s "{serial}"'
    output = subprocess.run(cmd, capture_output=True, shell=True, text=True)
    if "SUCCESS!" in output.stdout:
        success = "true"
        trigger_reload()
    else:
        success = "false"
    return jsonify(
        data={"output": output.stdout.replace("\n", "<br>"), "success": success}
    )
