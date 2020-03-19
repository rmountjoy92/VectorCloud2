import anki_vector
from vectorcloud.main.models import Vectors
from vectorcloud.main.utils import run_plugin


class Plugin:
    def __init__(self, *args, **kwargs):
        # parse user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted options
        if not hasattr(self, "vector_id"):
            vector = Vectors.query.first()
            self.vector_id = vector.id
        if not hasattr(self, "command"):
            self.command = "undock"
        if not hasattr(self, "log"):
            self.log = "true"

    def interface_data(self):
        interface_data = {
            "plugin_settings": [
                {
                    "name": "vector_id",
                    "default": "first entry",
                    "description": "which vector id to use for the command",
                },
                {
                    "name": "command",
                    "default": "undock",
                    "description": "options are: dock, undock",
                },
                {
                    "name": "log",
                    "default": "true",
                    "description": "create a log item when plugin is ran",
                },
            ],
            "plugin_description": "Functions related to Vector's charger",
            "plugin_icons": [
                {"mdi_class": "home", "class": "dock-btn", "tooltip": "Dock"},
                {
                    "mdi_class": "home",
                    "class": "undock-btn theme-primary-text color-ignore hide",
                    "tooltip": "Undock",
                },
            ],
            "plugin_js": ["charger.js"],
            "plugin_dependencies": ["logbook", "stats"],
        }
        return interface_data

    def run(self):
        # get the vector's database entry
        vector = Vectors.query.filter_by(id=self.vector_id).first()

        # try to send to command to the robot, log the result
        with anki_vector.Robot(vector.serial) as robot:
            try:
                if self.command == "dock":
                    output = str(robot.behavior.drive_on_charger())
                elif self.command == "undock":
                    output = str(robot.behavior.drive_off_charger())
            except Exception as e:
                output = e

        if self.log == "true":
            info = f"vector_id: {self.vector_id} \n \n output: {output}"
            run_plugin(
                "logbook",
                {
                    "name": f"{vector.name} ran {self.command}",
                    "vector_id": vector.id,
                    "info": info,
                    "log_type": "success",
                },
            )
        run_plugin("stats", {"vector_id": vector.id, "log": False})
        return output
