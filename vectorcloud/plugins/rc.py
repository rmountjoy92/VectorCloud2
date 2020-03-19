import io
import anki_vector
from flask import Response, url_for, request
from vectorcloud import app
from vectorcloud.main.models import Vectors
from vectorcloud.main.utils import run_plugin


class Plugin:
    def __init__(self, *args, **kwargs):
        # parse user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted options
        if not hasattr(self, "vector_id"):
            self.vector_id = "all"
        if not hasattr(self, "log"):
            self.log = "true"

    def interface_data(self):
        interface_data = {
            "plugin_description": "None",
            "plugin_icons": [
                {
                    "mdi_class": "games",
                    "class": "rc-panel-btn",
                    "tooltip": "Remote Control",
                }
            ],
            "plugin_panels": [{"class": "rc-panel", "template": "rc-panel.html"}],
            "plugin_js": ["rc.js"],
            "plugin_dependencies": ["logbook"],
        }
        return interface_data

    def on_startup(self):
        @app.route("/get_video_feed_url")
        def get_video_feed_url():
            vector_id = request.args.get("vector_id")
            url = url_for("video_feed", vector_id=vector_id)
            return url

        @app.route("/video_feed?<vector_id>")
        def video_feed(vector_id):
            return Response(
                self.stream_video(vector_id),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

    def stream_video(self, vector_id):
        vector = Vectors.query.filter_by(id=vector_id).first()
        robot = anki_vector.Robot(vector.serial)
        robot.connect()
        robot.camera.init_camera_feed()
        while True:
            image = robot.camera.latest_image.raw_image
            img_io = io.BytesIO()
            image.save(img_io, "PNG")
            img_io.seek(0)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/png\r\n\r\n" + img_io.getvalue() + b"\r\n"
            )
        robot.disconnect()

    def run(self):
        run_plugin(
            "logbook", {"name": "rc does not have a run function", "log_type": "fail"},
        )
