from flask import request, Response
from flask_restful import Resource
from vectorcloud.version import vectorcloud_version
from vectorcloud.main.utils import stream_video
from vectorcloud.plugins.utils import run_plugin


"""
resources.py
====================================
The REST API endpoints.
"""


class Version(Resource):
    """
    This resource will return the current version of VectorCloud

    :url: /api/version
    """

    def get(self):
        api_key = "123456789"
        if request.args["api_key"] == api_key:
            return {"version": vectorcloud_version}
        else:
            return {"response": "Unauthorized"}


class RunPlugin(Resource):
    """
    This resources calls the function: :func:`.robot_do`

    :url: /api/run
    """

    def get(self):
        api_key = "123456789"
        if request.args["api_key"] == api_key:
            options = {}
            for key, value in request.args.items():
                options[key] = value
            output = run_plugin(request.args.get("name"), options)
            return output
        else:
            return {"response": "Unauthorized"}
        return "ok"


class VideoFeed(Resource):
    """
    This resources calls the function: :func:`.robot_do`

    :url: /api/video_feed
    """

    def get(self):
        api_key = "123456789"
        if request.args["api_key"] == api_key:
            return Response(
                stream_video(request.args["vector_id"]),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )
        else:
            return {"response": "Unauthorized"}
