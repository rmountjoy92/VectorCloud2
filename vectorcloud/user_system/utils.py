from vectorcloud import db, bcrypt
from vectorcloud.user_system.models import User


def add_user_func(username, password):
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return user


def change_password(user_id, new_password):
    user = User.query.filter_by(id=user_id).first()
    hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
    user.password = hashed_password
    db.session.merge(user)
    db.session.commit()
