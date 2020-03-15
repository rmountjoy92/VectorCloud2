import anki_vector
from vectorcloud.main.models import Vectors
from vectorcloud.plugins.utils import run_plugin


class Plugin:
    def __init__(self, *args, **kwargs):
        # this blocks the user from being able to delete this plugin, as it is required
        # for VectorCloud to function
        self.vc_required = True

        # tell vectorcloud what settings are available for this plugin
        self.plugin_settings = [
            {
                "name": "vector_id",
                "default": "all",
                "description": "which vector id to use for the command",
            },
            {
                "name": "text_to_say",
                "default": "Hello World",
                "description": "the text for vector to say",
            },
            {
                "name": "log",
                "default": "True",
                "description": "create a log item when plugin is ran",
            },
        ]

        # describe what this plugin does
        self.plugin_description = "Make Vector say the given text"

        # this parses the user supplied plugin settings
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # set defaults for omitted settings
        if not hasattr(self, "vector_id"):
            vector = Vectors.query.first()
            self.vector_id = vector.id
        if not hasattr(self, "text_to_say"):
            self.text_to_say = "Hello World"
        if not hasattr(self, "log"):
            self.log = True

    def run(self):
        # get the vector's database entry
        vector = Vectors.query.filter_by(id=self.vector_id).first()

        # try to send to command to the robot, log the result if log is True
        with anki_vector.Robot(vector.serial) as robot:
            try:
                output = str(robot.behavior.say_text(self.text_to_say))
            except Exception as e:
                output = e
        if self.log is True:
            info = (
                f"text_to_say: {self.text_to_say} \n \n"
                f"vector_id: {self.vector_id} \n \n"
                f"output: {output}"
            )
            run_plugin(
                "log",
                {
                    "name": f"{vector.name} ran say",
                    "vector_id": vector.id,
                    "info": info,
                    "log_type": "success",
                },
            )
        return output
