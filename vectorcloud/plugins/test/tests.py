import anki_vector
from flask_socketio import emit


def hello_world(serial):
    with anki_vector.Robot(serial) as robot:
        robot.behavior.say_text("test")
    emit("server_message", {"html": "hello world complete!"})
