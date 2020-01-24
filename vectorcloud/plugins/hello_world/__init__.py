import anki_vector
from flask_socketio import emit
from vectorcloud.main.models import Vectors

vector = Vectors.query.first()

with anki_vector.Robot(vector.serial) as robot:
    robot.behavior.say_text("Hello World")
    emit("server_message", {"html": "hello world complete!"})
