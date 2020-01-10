import os
from flask import request
from flask_restful import Resource
from vectorcloud.version import vectorcloud_version
from vectorcloud.main.utils import get_stats, robot_do

api_key = "123456789"


class Version(Resource):
    def put(self):
        if request.form["api_key"] == api_key:
            return {"version": vectorcloud_version}
        else:
            return {"response": "Unauthorized"}


class Stats(Resource):
    def put(self):
        if request.form["api_key"] == api_key:
            response = get_stats(vector_id=request.form["vector_id"], return_stats=True)
            return {"stats": response}
        else:
            return {"response": "Unauthorized"}


class RobotDo(Resource):
    def put(self):
        if request.form["api_key"] == api_key:
            response = robot_do(
                commands=request.form["commands"],
                vector_id=request.form["vector_id"],
                emit_logbook=False,
            )
            return {"output": response}
        else:
            return {"response": "Unauthorized"}
