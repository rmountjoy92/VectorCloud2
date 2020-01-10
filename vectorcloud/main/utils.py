import anki_vector
from flask_socketio import emit
from flask import render_template
from datetime import datetime
from vectorcloud import socketio, db
from vectorcloud.main.moment import create_moment
from vectorcloud.main.models import Logbook, Vectors


# --------------------------------------------------------------------------------------
# STATS FUNCTIONS
# --------------------------------------------------------------------------------------
def get_stats(vector):
    response = {"ip": vector.ip, "name": vector.name, "serial": vector.serial}

    # get robot name and ip from config file
    # f = open(sdk_config_file, "r")
    # serial = f.readline()
    # serial = serial.replace("]", "")
    # serial = serial.replace("[", "")
    # serial = serial.replace("\n", "")
    # f.close()
    # config.read(sdk_config_file)
    # response["ip"] = config.get(serial, "ip")
    # response["name"] = config.get(serial, "name")

    # get results from battery state and version state
    robot = anki_vector.Robot(vector.serial, behavior_control_level=None)
    try:
        robot.connect()
    except Exception as e:
        return e

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

    logbook_log(
        name=f"{vector.name} reported his stats", log_type="success", info=str(response)
    )
    return response


@socketio.on("request_stats")
def handle_stats_request(json):
    if "vector_id" not in json:
        json["vector_id"] = "all"

    if json["vector_id"] == "all":
        vectors = Vectors.query.all()
    else:
        vectors = Vectors.query.filter_by(id=json["vector_id"]).all()

    for vector in vectors:
        response = get_stats(vector)
        try:
            emit("stats", response)
        except TypeError:
            emit(
                "server_message",
                {
                    "html": f"ERROR! {response.__class__.__name__}",
                    "classes": "theme-warning",
                },
            )


# --------------------------------------------------------------------------------------
# ROBOT DO FUNCTIONS
# --------------------------------------------------------------------------------------
def robot_do(commands, vector_id):
    vector = Vectors.query.filter_by(id=vector_id).first()
    logbook_log(name=f"You sent {vector.name} {commands}")

    robot = anki_vector.Robot(vector.serial)
    try:
        robot.connect()
    except Exception as e:
        logbook_log(
            name=f"Connection to {vector.name} failed!", info=f"{e}", log_type="fail"
        )

    response = ""
    for command in commands.split(","):
        try:
            response += f"{str(eval(command))}\n"
            logbook_log(
                name=f"{vector.name} completed {commands}",
                info=response,
                log_type="success",
            )
        except Exception as e:
            logbook_log(
                name=f"Command {command} to {vector.name} failed!",
                info=f"{e}",
                log_type="fail",
            )

    robot.disconnect()


@socketio.on("request_robot_do")
def handle_robot_do(json):
    if "vector_id" not in json:
        json["vector_id"] = 1

    robot_do(json["command"], json["vector_id"])


# --------------------------------------------------------------------------------------
# LOGBOOK FUNCTIONS
# --------------------------------------------------------------------------------------
def get_logbook_html():
    logbook_items = Logbook.query.order_by(Logbook.dt.desc()).all()
    for item in logbook_items:
        item = create_moment(item)
    html = render_template("main/logbook-rows.html", logbook_items=logbook_items)
    return html


def logbook_log(name, info=None, log_type=None):
    log = Logbook()
    log.name = name
    log.info = info
    log.dt = datetime.now()
    log.log_type = log_type
    db.session.add(log)
    db.session.commit()
    emit("logbook", get_logbook_html())


@socketio.on("request_logbook")
def handle_logbook_request():
    emit("logbook", get_logbook_html())


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
