import anki_vector
from flask_socketio import emit
from flask import render_template
from flask_login import current_user
from datetime import datetime
from vectorcloud import socketio, db
from vectorcloud.main.moment import create_moment
from vectorcloud.main.models import Logbook, Vectors


# --------------------------------------------------------------------------------------
# STATS FUNCTIONS
# --------------------------------------------------------------------------------------
def get_stats(vector_id, return_stats=False):
    if vector_id == "all":
        vectors = Vectors.query.all()
    else:
        vectors = Vectors.query.filter_by(id=vector_id).all()

    for vector in vectors:
        response = {"ip": vector.ip, "name": vector.name, "serial": vector.serial}
        robot = anki_vector.Robot(vector.serial, behavior_control_level=None)
        try:
            robot.connect()
        except Exception as e:
            if return_stats is True:
                return str(e)
            else:
                logbook_log(
                    name=f"Connection to {vector.name} failed!",
                    info=f"{e}",
                    log_type="fail",
                )
            continue

        try:
            version_state = robot.get_version_state()
            battery_state = robot.get_battery_state()
        except Exception as e:
            if return_stats is True:
                return str(e)
            else:
                logbook_log(
                    name=f"{vector.name} failed to report stats!",
                    info=f"{e}",
                    log_type="fail",
                )
            continue

        robot.disconnect()

        response["version"] = version_state.os_version
        response["battery_voltage"] = battery_state.battery_volts
        response["battery_level"] = battery_state.battery_level
        response["status_charging"] = battery_state.is_on_charger_platform
        response["cube_battery_level"] = battery_state.cube_battery.level
        response["cube_id"] = battery_state.cube_battery.factory_id
        response["cube_battery_volts"] = battery_state.cube_battery.battery_volts

        if return_stats is True:
            return response
        else:
            logbook_log(
                name=f"{vector.name} reported its stats",
                log_type="success",
                info=str(response),
            )
            emit("stats", response)


@socketio.on("request_stats")
def handle_stats_request(json):
    if "vector_id" not in json:
        json["vector_id"] = "all"

    get_stats(json["vector_id"])


# --------------------------------------------------------------------------------------
# ROBOT DO FUNCTIONS
# --------------------------------------------------------------------------------------
def robot_do(commands, vector_id, emit_logbook=True):
    vector = Vectors.query.filter_by(id=vector_id).first()

    command_list = commands.split(",")
    if len(command_list) > 1:
        commands_str = f"{len(command_list)} commands"
    else:
        commands_str = commands

    try:
        user_fname = current_user.fname
    except AttributeError:
        user_fname = "The API"
    nl = "\n"
    logbook_log(
        name=f"{user_fname} sent {vector.name} {commands_str}",
        info=f"COMMANDS:\n{commands.replace(',', nl)}",
        emit_logbook=emit_logbook,
    )

    robot = anki_vector.Robot(vector.serial)
    try:
        robot.connect()
    except Exception as e:
        logbook_log(
            name=f"Connection to {vector.name} failed!",
            info=f"{e}",
            log_type="fail",
            emit_logbook=emit_logbook,
        )
        return f"{e}"

    response = ""
    i = 1
    for command in command_list:
        try:
            response += f"COMMAND: {command}\nRESPONSE: {str(eval(command))}\n"
            if i == len(command_list):
                logbook_log(
                    name=f"{vector.name} completed {commands_str}",
                    info=response,
                    log_type="success",
                    emit_logbook=emit_logbook,
                )
        except Exception as e:
            response += f"{e}\n"
            logbook_log(
                name=f"Command {command} to {vector.name} failed!",
                info=f"{e}",
                log_type="fail",
                emit_logbook=emit_logbook,
            )
        i += 1

    robot.disconnect()
    if not emit_logbook:
        return response
    else:
        get_stats(vector.id)


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


def logbook_log(name, info=None, log_type=None, emit_logbook=True):
    log = Logbook()
    log.name = name
    log.info = info
    log.dt = datetime.now()
    log.log_type = log_type
    db.session.add(log)
    db.session.commit()
    if emit_logbook:
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
