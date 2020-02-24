from vectorcloud import db, login_manager
from flask_login import UserMixin


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


db.create_all()
db.session.commit()
