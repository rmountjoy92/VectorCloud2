import anki_vector
from flask_socketio import emit
from vectorcloud.main.models import Vectors
from vectorcloud.plugins.utils import run_plugin


class Plugin:
    def __init__(self, *args, **kwargs):

        # tell vectorcloud what settings are available for this plugin
        self.plugin_settings = ["vector_id"]

        # parse user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted options
        if not hasattr(self, "vector_id"):
            self.vector_id = "all"

    def run(self):
        if self.vector_id == "all":
            vectors = Vectors.query.all()
        else:
            vectors = [Vectors.query.filter_by(id=self.vector_id).first()]

        responses = []
        for vector in vectors:
            response = {"ip": vector.ip, "name": vector.name, "serial": vector.serial}
            robot = anki_vector.Robot(vector.serial, behavior_control_level=None)
            try:
                robot.connect()
            except Exception as e:
                run_plugin(
                    "log",
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
            robot.disconnect()

            response["version"] = version_state.os_version
            response["battery_voltage"] = battery_state.battery_volts
            response["battery_level"] = battery_state.battery_level
            response["status_charging"] = battery_state.is_on_charger_platform
            response["cube_battery_level"] = battery_state.cube_battery.level
            response["cube_id"] = battery_state.cube_battery.factory_id
            response["cube_battery_volts"] = battery_state.cube_battery.battery_volts

            emit("stats", response, broadcast=True, namespace="/")
            run_plugin(
                "log",
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
