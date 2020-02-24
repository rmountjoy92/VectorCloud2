from vectorcloud import db
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

    vector_id = db.Column(db.Integer, db.ForeignKey("vectors.id"))


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
    logbook_items = db.relationship(
        "Logbook", backref="vector", order_by="desc(Logbook.dt)"
    )


db.create_all()
db.session.commit()
