from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
)
from wtforms.validators import DataRequired, EqualTo, Length, Email


class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired()])

    password = PasswordField(
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters."),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )

    confirm_password = PasswordField(validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired()])

    remember = BooleanField("Remember Me")


class VectorForm(FlaskForm):
    anki_email = StringField(validators=[DataRequired(), Email()])
    anki_password = PasswordField("Password", validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
    ip = StringField(validators=[DataRequired()])
    serial = StringField(validators=[DataRequired()])
