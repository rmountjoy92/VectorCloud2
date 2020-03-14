import anki_vector
from vectorcloud.main.models import Vectors
from vectorcloud.plugins.utils import run_plugin, CaptureOutput


class Plugin:
    def __init__(self, *args, **kwargs):

        # tell vectorcloud what settings are available for this plugin
        self.plugin_settings = ["vector_id", "text_to_say"]

        # describe what this plugin does
        self.plugin_description = "Make Vector say the given text"

        # parse user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted options
        if not hasattr(self, "vector_id"):
            vector = Vectors.query.first()
            self.vector_id = vector.id
        if not hasattr(self, "text_to_say"):
            self.text_to_say = "Hello World"

    def run(self):
        # get the vector's database entry
        vector = Vectors.query.filter_by(id=self.vector_id).first()

        # try to send to command to the robot, log the result
        with CaptureOutput() as output:
            with anki_vector.Robot(vector.serial) as robot:
                output = str(robot.behavior.say_text(self.text_to_say))
                run_plugin(
                    "log",
                    {
                        "name": f"{vector.name} ran say.",
                        "vector_id": vector.id,
                        "info": output,
                        "log_type": "success",
                    },
                )

        return output
