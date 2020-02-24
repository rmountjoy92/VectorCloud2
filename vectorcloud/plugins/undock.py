import anki_vector
from vectorcloud.main.models import Vectors
from vectorcloud.plugins.utils import run_plugin


class Plugin:
    def __init__(self, *args, **kwargs):

        # tell vectorcloud what settings are available for this plugin
        self.plugin_settings = ["vector_id"]

        # describe what this plugin does
        self.plugin_description = "Undock vector"

        # parse user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted options
        if not hasattr(self, "vector_id"):
            vector = Vectors.query.first()
            self.vector_id = vector.id

    def run(self):
        # get the vector's database entry
        vector = Vectors.query.filter_by(id=self.vector_id).first()

        # try to send to command to the robot, log the result
        try:
            with anki_vector.Robot(vector.serial) as robot:
                output = str(robot.behavior.drive_off_charger())
                run_plugin(
                    "log",
                    {
                        "name": f"{vector.name} undocked",
                        "vector_id": vector.id,
                        "info": output,
                        "log_type": "success",
                    },
                )
        except Exception as e:
            run_plugin(
                "log",
                {
                    "name": f"{vector.name} failed to undock",
                    "vector_id": vector.id,
                    "info": str(e),
                    "log_type": "fail",
                },
            )
            return str(e)

        return output
