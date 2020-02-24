import io
import anki_vector
from anki_vector.util import distance_mm, speed_mmps, degrees
from flask import render_template
from vectorcloud import socketio
from vectorcloud.main.moment import create_moment
from vectorcloud.main.models import Logbook, Vectors


# --------------------------------------------------------------------------------------
# LOGBOOK FUNCTIONS
# --------------------------------------------------------------------------------------
def get_logbook_html(vector):
    for item in vector.logbook_items:
        item = create_moment(item)
    html = render_template("main/logbook-rows.html", logbook_items=vector.logbook_items)
    return html


# --------------------------------------------------------------------------------------
# VIDEO STREAMING FUNCTIONS
# --------------------------------------------------------------------------------------
def stream_video(vector_id):
    vector = Vectors.query.filter_by(id=vector_id).first()
    robot = anki_vector.Robot(vector.serial)
    robot.connect()
    robot.camera.init_camera_feed()
    while True:
        image = robot.camera.latest_image.raw_image
        img_io = io.BytesIO()
        image.save(img_io, "PNG")
        img_io.seek(0)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/png\r\n\r\n" + img_io.getvalue() + b"\r\n"
        )


# --------------------------------------------------------------------------------------
# REMOTE CONTROL
# --------------------------------------------------------------------------------------
@socketio.on("start_rc")
def handle_start_rc(json):
    vector = Vectors.query.filter_by(id=json["vector_id"]).first()
    while True:
        socketio.on_event("rc_key", remote_control)


def remote_control(keys, serial):
    with anki_vector.Robot(serial) as robot:
        move_dist = distance_mm(200)
        if "shift" in keys:
            drive_speed = speed_mmps(100)
            turn_speed = 100
        else:
            drive_speed = speed_mmps(50)
            turn_speed = 50
        if "forward" in keys:
            robot.behavior.drive_straight(move_dist, drive_speed)
        elif "backward" in keys:
            robot.behavior.drive_straight(move_dist * -1, drive_speed)
        if "right" in keys:
            robot.behavior.turn_in_place(degrees(-90))
        if "left" in keys:
            robot.behavior.turn_in_place(degrees(90))


def input_test():
    while True:
        keys = []
        key = input("enter direction:")
        if "w" in key:
            keys.append("forward")
        if "s" in key:
            keys.append("backward")
        if "a" in key:
            keys.append("left")
        if "d" in key:
            keys.append("right")
        remote_control(keys, "009087e0")


# --------------------------------------------------------------------------------------
# UTILITY/MISC FUNCTIONS
# --------------------------------------------------------------------------------------
def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def database_init():
    pass
