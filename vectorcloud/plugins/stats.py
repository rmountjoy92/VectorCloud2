import anki_vector
from flask_socketio import emit
from vectorcloud import socketio
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
            "plugin_settings": [
                {
                    "name": "vector_id",
                    "default": "all",
                    "description": "which vector id to use for the command",
                },
                {
                    "name": "log",
                    "default": "true",
                    "description": "create a log item when plugin is ran",
                },
            ],
            "plugin_description": "None",
            "plugin_icons": [
                {
                    "mdi_class": "refresh",
                    "class": "stats-refresh-btn",
                    "tooltip": "Refesh stats",
                },
                {"mdi_class": "info", "class": "stats-info-btn", "tooltip": "Stats"},
                {"mdi_class": "pages", "class": "stats-cube-btn", "tooltip": "Cube"},
                {
                    "mdi_class": "battery_full",
                    "class": "stats-battery-btn color-ignore",
                    "tooltip": "Battery",
                },
            ],
            "plugin_panels": [
                {"class": "stats-info-panel", "template": "stats-info-panel.html"},
                {"class": "stats-cube-panel", "template": "stats-cube-panel.html"},
                {
                    "class": "stats-battery-panel",
                    "template": "stats-battery-panel.html",
                },
            ],
            "plugin_js": ["stats.js"],
            "plugin_dependencies": ["logbook", "cube"],
        }
        return interface_data

    def on_startup(self):
        @socketio.on("request_stats")
        def handle_stats_request(json):
            if "vector_id" not in json:
                json["vector_id"] = "all"

            run_plugin("stats", {"vector_id": json["vector_id"]})

    def run(self):
        if self.vector_id == "all":
            vectors = Vectors.query.all()
        else:
            vectors = [Vectors.query.filter_by(id=self.vector_id).first()]

        responses = []
        for vector in vectors:
            response = {
                "id": vector.id,
                "ip": vector.ip,
                "name": vector.name,
                "serial": vector.serial,
            }
            robot = anki_vector.Robot(vector.serial, behavior_control_level=None)
            try:
                robot.connect()
            except Exception as e:
                run_plugin(
                    "logbook",
                    {
                        "name": f"{vector.name} failed to connect",
                        "vector_id": vector.id,
                        "info": str(e),
                        "log_type": "fail",
                    },
                )
                continue

            version_state = robot.get_version_state()
            battery_state = robot.get_battery_state()

            response["version"] = version_state.os_version
            response["battery_voltage"] = battery_state.battery_volts
            response["battery_level"] = battery_state.battery_level
            response["status_charging"] = battery_state.is_on_charger_platform
            response["cube_battery_level"] = battery_state.cube_battery.level
            response["cube_id"] = battery_state.cube_battery.factory_id
            response["cube_battery_volts"] = battery_state.cube_battery.battery_volts

            emit("stats", response, broadcast=True, namespace="/")
            if self.log == "true":
                run_plugin(
                    "logbook",
                    {
                        "name": f"{vector.name} reported its stats",
                        "vector_id": vector.id,
                        "info": str(response),
                        "log_type": "success",
                    },
                )
            responses.append(response)

        if len(responses) > 1:
            return responses
        else:
            return response
