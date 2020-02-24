from datetime import datetime
from flask_socketio import emit
from vectorcloud import db
from vectorcloud.main.models import Logbook, Vectors
from vectorcloud.main.utils import get_logbook_html


class Plugin:
    def __init__(self, *args, **kwargs):

        # tell vectorcloud what settings are available for this plugin
        self.plugin_settings = ["name", "vector_id", "info", "log_type", "emit_only"]

        # give vectorcloud access to the description
        self.plugin_description = (
            "Create a logbook item and update the UI, optionally just update the UI"
        )

        # parse user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted options
        if not hasattr(self, "name"):
            self.name = "Unnamed logbook item"
        if not hasattr(self, "vector_id"):
            self.vector_id = None
        if not hasattr(self, "info"):
            self.info = None
        if not hasattr(self, "log_type"):
            self.log_type = None
        if not hasattr(self, "emit_only"):
            self.emit_only = False

    def run(self):
        if self.emit_only is False:
            log = Logbook()
            log.name = self.name
            log.info = self.info
            log.dt = datetime.now()
            log.log_type = self.log_type
            log.vector = Vectors.query.filter_by(id=self.vector_id).first()
            db.session.add(log)
            db.session.commit()

        html_dict = {}
        for vector in Vectors.query.all():
            html_dict[vector.id] = get_logbook_html(vector)

        emit("logbook", html_dict, broadcast=True, namespace="/")
        return "ok"
