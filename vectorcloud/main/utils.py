import io
import anki_vector
from flask_socketio import emit
from flask import render_template
from flask_login import current_user
from datetime import datetime
from vectorcloud import socketio, db
from vectorcloud.main.moment import create_moment
from vectorcloud.main.models import Logbook, Vectors, Scripts


# --------------------------------------------------------------------------------------
# STATS FUNCTIONS
# --------------------------------------------------------------------------------------
def get_stats(vector_id, return_stats=False):
    """
    This function is the central function for getting statistic data from Vector.
    It uses whatever SDK commands that I can find that return stats. When called
    it will either return the stats, or emit them to the web client for updating the ui,
    depending on the state of 'return_stats'

    :type vector_id: int
    :param vector_id: The database ID for the Vector you want to control. If empty this defaults to '1', which is the first Vector registered in the database

    :type return_stats: bool
    :param return_stats: Default is True, if set to False, the server will not emit the stats to the web client, instead it will return the response.

    :return: If return_stats is set to True, this function will return the response of the function as a dictionary object. If return_stats is False, this function will return nothing, but emit the stats to the web client
    """
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
def robot_do(commands, vector_id, emit_logbook=True, args=None):
    """
    This function is the central function for passing commands to Vector. It is also
    responsible for launching scripts, which in turn can import and call plugins.
    Commands are given to function as a comma separated string - meaning you can send
    multiple commands - just put a comma between them, no spaces. Arguments are provided
    by the script or the user and are applied to the namespace before the commands are
    run, simply by calling them like so: x = 1. Each command is run and logged in the
    logbook item, if it run successfully, the output is logged, if it fails, the error
    is logged. When it's done it either returns the result of the commands in a string
    or it emits the logbook item to the web client, depending on the state of
    emit_logbook. It then runs get_stats to update the web client with vector's new stats.

    :type commands: str
    :param commands: SDK/VectorCloud commands to be processed by robot_do in comma separated format

    :type vector_id: int
    :param vector_id: The database ID for the Vector you want to control. If empty this defaults to '1', which is the first Vector registered in the database

    :type emit_logbook: bool
    :param emit_logbook: Default is True, if set to False, the server will not refresh the logbook in the web client.

    :type args: str
    :param args: Arguments allow the command/script to set variables before executing commands. These are also in comma separated format.

    :return: If emit_logbook is set to False, this function will return the response of all executed commands combined into one string. If emit_logbook is True, this function will return nothing, but request the logbook to update the web client
    """
    vector = Vectors.query.filter_by(id=vector_id).first()

    if "script:" in commands:
        script_id_or_name = commands.split(":")[1]
        if "?" in script_id_or_name:
            args = script_id_or_name.split("?")[1]
            script_id_or_name = script_id_or_name.split("?")[0]
        script = Scripts.query.filter_by(id=script_id_or_name).first()
        if not script:
            script = Scripts.query.filter_by(name=script_id_or_name).first()
        command_list = script.commands.split(",")
        commands_str = script.name
    else:
        command_list = commands.split(",")
        if len(command_list) > 1:
            commands_str = f"{len(command_list)} commands"
        else:
            commands_str = commands
    if args:
        for arg in args.split(","):
            command_list.insert(0, arg)
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
            if any(x in command for x in ["=", "from ", "import"]):
                response += f"COMMAND: {command}\n"
                exec(command)
            else:
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
    """
    This function writes to the VectorCloud logbook. Optionally, it emits the logbook html to the web client to replace the current representation of the logbook in the web client.

    :type name: str
    :param name: a title for the logbook entry

    :type info: str
    :param info: info for the logbook entry (often used for storing the output of commands)

    :type log_type: str
    :param log_type: log type, changes some css classes in the web client, options are 'success', 'fail', None

    :type emit_logbook: bool
    :param emit_logbook: If emit_logbook is set to False, this function will return nothing. If emit_logbook is True, this function will emit the logbook to the web client

    """
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


@socketio.on("logbook_log")
def handle_logbook_log(json):
    if "emit_logbook" not in json:
        json["emit_logbook"] = True

    logbook_log(
        name=json["name"], log_type=json["log_type"], emit_logbook=json["emit_logbook"]
    )


# --------------------------------------------------------------------------------------
# VIDEO STREAMING FUNCTIONS
# --------------------------------------------------------------------------------------
def stream_video(vector_id):
    vector = Vectors.query.filter_by(id=vector_id).first()
    robot = anki_vector.Robot(vector.serial)
    robot.connect()
    robot.camera.init_camera_feed()
    logbook_log(
        name=f"{vector.name} has started streaming.",
        log_type="success",
        emit_logbook=False,
    )
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
# SCRIPTS FUNCTIONS
# --------------------------------------------------------------------------------------
def add_edit_script(name, description, commands, script_id=None):
    """
    This function is what adds and edits scripts to the vectorcloud database. It is the basis for how plugins are installed.

    :type name: str
    :param name: Name of script

    :type description: str
    :param description: Short description of what script does

    :type commands: str
    :param commands: SDK/VectorCloud commands to be processed by robot_do in comma separated format

    :type script_id: int
    :param script_id: database id for script

    :return: The script database object as a dict
    """
    commands = commands.replace("\n", ",")
    if script_id:
        script = Scripts.query.filter_by(id=script_id).first()
    else:
        script = Scripts()

    script.name = name
    script.description = description
    script.commands = commands
    db.session.merge(script)
    db.session.commit()
    return row2dict(script)


@socketio.on("add_edit_script")
def handle_add_edit_script(json):
    if "script_id" not in json:
        json["script_id"] = None

    script = add_edit_script(
        name=json["name"],
        description=json["description"],
        commands=json["commands"],
        script_id=json["script_id"],
    )


def get_scripts_html():
    scripts = Scripts.query.all()
    html = render_template("main/scripts-rows.html", scripts=scripts)
    return html


@socketio.on("request_scripts")
def handle_scripts_request():
    emit("scripts", get_scripts_html())


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
