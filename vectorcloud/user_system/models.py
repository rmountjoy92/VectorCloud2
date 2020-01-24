from flask import redirect, url_for
from vectorcloud import db, login_manager, bcrypt, admin
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView


# Models-----------------------------------------------------------------------
# -----------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    """
    int - database assigned ID
    """

    email = db.Column(db.String(120), unique=True, nullable=False)
    """
    str - email address for login
    """

    password = db.Column(db.String(60), nullable=False)
    """
    str - password for login
    """

    fname = db.Column(db.String(), nullable=False)
    """
    str - user's first name
    """

    lname = db.Column(db.String())
    """
    str - user's last name
    """

    role = db.Column(db.String(), nullable=False)
    """
    str - the user's permission level
    """


class UserView(ModelView):
    column_exclude_list = ["password"]
    column_display_pk = True

    def on_model_change(self, form, model, is_created):
        hashed_password = bcrypt.generate_password_hash(model.password).decode("utf-8")
        model.password = hashed_password

    def is_accessible(self):
        return current_user.role in ["superadmin", "admin"]

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("permission_denied.index"))
    column_searchable_list = [
        "id",
        "email",
        "fname",
        "lname",
        "role",
    ]
    column_filters = [
        "id",
        "email",
        "fname",
        "lname",
        "role",
    ]


admin.add_view(UserView(User, db.session))

db.create_all()
db.session.commit()
