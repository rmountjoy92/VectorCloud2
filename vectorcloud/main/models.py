from vectorcloud import db


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
    str - string of commands to be sent to robot_do formatted as comma separated string
    """

    args = db.Column(db.String())
    """
    str - string of default arguments for scripts formatted as comma separated string
    """


db.create_all()
db.session.commit()
