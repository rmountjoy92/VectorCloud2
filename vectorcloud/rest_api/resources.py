from flask import request
from flask_restful import Resource
from vectorcloud.version import vectorcloud_version
from vectorcloud.main.utils import get_stats, robot_do


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

    def put(self):
        api_key = "123456789"
        if request.form["api_key"] == api_key:
            return {"version": vectorcloud_version}
        else:
            return {"response": "Unauthorized"}


class Stats(Resource):
    """
    This resources calls the function: :func:`.get_stats`

    :url: /api/stats
    """

    def put(self):
        api_key = "123456789"
        if request.form["api_key"] == api_key:
            response = get_stats(vector_id=request.form["vector_id"], return_stats=True)
            return {"stats": response}
        else:
            return {"response": "Unauthorized"}


class RobotDo(Resource):
    """
    This resources calls the function: :func:`.robot_do`

    :url: /api/robot_do
    """

    def put(self):
        api_key = "123456789"
        if request.form["api_key"] == api_key:
            response = robot_do(
                commands=request.form["commands"],
                vector_id=request.form["vector_id"],
                args=request.form["args"],
                emit_logbook=False,
            )
            return {"output": response}
        else:
            return {"response": "Unauthorized"}
