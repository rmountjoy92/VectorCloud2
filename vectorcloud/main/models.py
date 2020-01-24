from vectorcloud import db, admin
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import TextAreaField


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    """
    int - database assigned ID
    """

    name = db.Column(db.String())
    """
    str - name of file
    """

    path = db.Column(db.String())
    """
    str - path where file currently resides
    """

    external_path = db.Column(db.String())
    """
    str - path from /vectorcloud
    """

    cache = db.Column(db.String())
    """
    str - cached name
    """

    folder = db.Column(db.String())
    """
    str - folder where file currently resides
    """


class Logbook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    """
    int - database assigned ID
    """

    name = db.Column(db.String())
    """
    str - logbook entry name
    """

    info = db.Column(db.String())
    """
    str - logbook entry info, often used for command output
    """

    dt = db.Column(db.String())
    """
    str - datetime object created at creation time
    """

    log_type = db.Column(db.String())
    """
    str - type of log, options are 'success', 'fail', None
    """


class LogbookView(ModelView):
    column_filters = [
        "name",
        "info",
        "dt",
        "log_type",
    ]
    column_searchable_list = [
        "name",
        "info",
        "dt",
        "log_type",
    ]
    can_create = False
    can_edit = False
    column_default_sort = ("dt", True)
    column_labels = dict(dt="Time", name="Name", info="Info", log_type="Log Type")
    can_set_page_size = True


admin.add_view(LogbookView(Logbook, db.session))


class Vectors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    """
    int - database assigned ID
    """

    serial = db.Column(db.String())
    """
    str - serial number from config file
    """

    cert_file = db.Column(db.String())
    """
    str - cert file from config file
    """

    ip = db.Column(db.String())
    """
    str - IP address of vector, from config file
    """

    name = db.Column(db.String())
    """
    str - name of vector, from config file
    """

    guid = db.Column(db.String())
    """
    str - guid from config file
    """

    custom_name = db.Column(db.String())
    """
    str - custom name to display in interface
    """

    description = db.Column(db.String())
    """
    str - custom description to display in interface
    """


class VectorsView(ModelView):
    column_searchable_list = [
        "serial",
        "ip",
        "name",
        "custom_name",
        "description",
    ]
    column_display_pk = True


admin.add_view(VectorsView(Vectors, db.session))


class Scripts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    """
    int - database assigned ID
    """

    name = db.Column(db.String())
    """
    str - name of script
    """

    description = db.Column(db.String())
    """
    str - short description of what script does
    """

    commands = db.Column(db.String())
    """
    str - string of commands to be sent to robot_do formatted as new-line separated string
    """

    args = db.Column(db.String())
    """
    str - string of default arguments for scripts formatted as new-line separated string
    """


class ScriptsView(ModelView):
    column_searchable_list = [
        "id",
        "name",
        "description",
    ]
    column_exclude_list = ["commands", "args"]
    column_display_pk = True
    can_set_page_size = True
    form_overrides = dict(
        description=TextAreaField, commands=TextAreaField, args=TextAreaField
    )
    form_widget_args = {
        "commands": {"style": "font-family: monospace;"},
        "args": {"style": "font-family: monospace;"},
    }


admin.add_view(ScriptsView(Scripts, db.session))

db.create_all()
db.session.commit()
