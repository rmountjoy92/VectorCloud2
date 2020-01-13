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
    /api/version
    """
    def put(self):
        api_key = "123456789"
        if request.form["api_key"] == api_key:
            return {"version": vectorcloud_version}
        else:
            return {"response": "Unauthorized"}


class Stats(Resource):
    """
    /api/stats
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
    /api/robot_do
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
