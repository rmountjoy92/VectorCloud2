from vectorcloud import socketio
from vectorcloud.plugins.utils import run_plugin


@socketio.on("run_plugin")
def handle_run_plugin(json):
    options = {}
    for key, value in json.items():
        if key != "name":
            options[key] = value

    run_plugin(json["name"], options)


@socketio.on("request_stats")
def handle_stats_request(json):
    if "vector_id" not in json:
        json["vector_id"] = "all"

    run_plugin("stats", {"vector_id": json["vector_id"]})


@socketio.on("request_logbook")
def handle_logbook_request():
    run_plugin("log", {"emit_only": True})


@socketio.on("logbook_log")
def handle_logbook_log(json):
    run_plugin(
        "log",
        {
            "name": json.get("name", None),
            "info": json.get("info", None),
            "log_type": json.get("log_type", None),
        },
    )
