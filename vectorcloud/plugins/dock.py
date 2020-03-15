import anki_vector
from vectorcloud.main.models import Vectors
from vectorcloud.plugins.utils import run_plugin


class Plugin:
    def __init__(self, *args, **kwargs):
        self.vc_required = True

        # tell vectorcloud what settings are available for this plugin
        self.plugin_settings = [
            {
                "name": "vector_id",
                "default": "first entry",
                "description": "which vector id to use for the command",
            },
            {
                "name": "log",
                "default": "True",
                "description": "create a log item when plugin is ran",
            },
        ]

        # describe what this plugin does
        self.plugin_description = "Dock vector"

        # parse user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted options
        if not hasattr(self, "vector_id"):
            vector = Vectors.query.first()
            self.vector_id = vector.id

        if not hasattr(self, "log"):
            self.log = True

    def run(self):
        # get the vector's database entry
        vector = Vectors.query.filter_by(id=self.vector_id).first()

        # try to send to command to the robot, log the result
        with anki_vector.Robot(vector.serial) as robot:
            try:
                output = str(robot.behavior.drive_on_charger())
            except Exception as e:
                output = e

        if self.log is True:
            info = f"vector_id: {self.vector_id} \n \n output: {output}"
            run_plugin(
                "log",
                {
                    "name": f"{vector.name} ran dock",
                    "vector_id": vector.id,
                    "info": info,
                    "log_type": "success",
                },
            )
        run_plugin("stats", {"vector_id": vector.id, "log": False})
        return output
