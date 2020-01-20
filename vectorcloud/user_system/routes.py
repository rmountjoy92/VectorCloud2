from flask import render_template, url_for, redirect, Blueprint
from flask_login import login_user, logout_user, current_user
from vectorcloud.user_system.forms import LoginForm, RegisterForm
from vectorcloud.user_system.models import User
from vectorcloud import bcrypt
from vectorcloud.main.utils import public_route

user_system = Blueprint("user_system", __name__)


# ------------------------------------------------------------------------------
# User system routes
# ------------------------------------------------------------------------------
# login page
@public_route
@user_system.route("/login", methods=["GET", "POST"])
def login():
    user = User.query.first()

    if not user:
        return redirect(url_for("user_system.welcome"))

    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            return redirect(url_for("main.home"))

        else:
            print("password was wrong")
            return redirect(url_for("user_system.login"))

    return render_template("user/login.html", title="Login", form=form)


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
@user_system.route("/add_user")
def add_user():
    pass
