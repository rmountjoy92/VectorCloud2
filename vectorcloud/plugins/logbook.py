from datetime import datetime
from flask import render_template
from flask_socketio import emit
from vectorcloud import db, socketio
from vectorcloud.main.models import Logbook, Vectors
from vectorcloud.main.moment import create_moment
from vectorcloud.main.utils import run_plugin


class Plugin:
    def __init__(self, *args, **kwargs):

        # parse user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted options
        if not hasattr(self, "name"):
            self.name = "Unnamed logbook item"
        if not hasattr(self, "vector_id"):
            self.vector_id = Vectors.query.first().id
        if not hasattr(self, "info"):
            self.info = None
        if not hasattr(self, "log_type"):
            self.log_type = None
        if not hasattr(self, "emit_only"):
            self.emit_only = False

    def interface_data(self):
        interface_data = {
            "plugin_settings": [
                {
                    "name": "name",
                    "default": "Unnamed logbook item",
                    "description": "title of the newly created log item",
                },
                {
                    "name": "vector_id",
                    "default": "first entry",
                    "description": "associate a vector to the log item",
                },
                {
                    "name": "info",
                    "default": "None",
                    "description": "optionally include description text for the log item",
                },
                {
                    "name": "emit_only",
                    "default": "False",
                    "description": "when true, no log item is created, but the logbook is still refreshed in the web client",
                },
            ],
            "plugin_description": "Create a logbook item and update the UI, optionally just update the UI",
            "plugin_icons": [
                {
                    "mdi_class": "timeline",
                    "class": "show-logbook-btn",
                    "tooltip": "Logbook",
                }
            ],
            "plugin_panels": [
                {"class": "logbook-panel", "template": "logbook-panel.html"},
            ],
            "plugin_js": ["logbook.js"],
        }
        return interface_data

    def get_html(self, vector):
        for item in vector.logbook_items:
            item = create_moment(item)
        html = render_template(
            "plugins/logbook-rows.html", logbook_items=vector.logbook_items
        )
        return html

    def on_startup(self):
        @socketio.on("request_logbook")
        def handle_logbook_request():
            run_plugin("logbook", {"emit_only": True})

        @socketio.on("logbook_log")
        def handle_logbook_log(json):
            run_plugin(
                "logbook",
                {
                    "name": json.get("name", None),
                    "info": json.get("info", None),
                    "log_type": json.get("log_type", None),
                },
            )

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
            html_dict[vector.id] = self.get_html(vector)

        emit("logbook", html_dict, broadcast=True, namespace="/")
        return "ok"
