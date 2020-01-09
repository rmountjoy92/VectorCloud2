import anki_vector
from flask_socketio import emit
from datetime import datetime
from vectorcloud import config, socketio, db
from vectorcloud.paths import sdk_config_file
from vectorcloud.main.models import Logbook, Vectors


# establishes routes decorated w/ @public_route as accessible while not signed
# in. See login and register routes for usage
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


def get_stats(vector_id):
    if vector_id == "all":
        vectors = Vectors.query.all()
    else:
        vectors = Vectors.query.filter_by(id=vector_id).all()
    for vector in vectors:
        response = {"ip": vector.ip, "name": vector.name}

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

        logbook_log(name=f"{vector.name} reported his stats")
        return response


@socketio.on("request_stats")
def handle_stats_request(json):
    if "vector_id" not in json:
        json["vector_id"] = 1

    response = get_stats(json["vector_id"])
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


# robot_do(): this function executes all commands in the command table in order
# with the condition of with anki_vector.Robot(args.serial) as robot:
# if there are commands in the commands in the command table, all you have to
# do to execute is redirect to /execute_commands/ and this function will be
# called. Output is sent to a flash message.
def robot_do(commands, vector_id):
    vector = Vectors.query.filter_by(id=vector_id).first()
    logbook_log(name=f"You sent {vector.name} {commands}")

    robot = anki_vector.Robot(vector.serial)
    try:
        robot.connect()
    except Exception as e:
        return e

    response = ""
    for command in commands.split(","):
        try:
            response += f"{str(eval(command))}\n"
        except Exception as e:
            response += f"Error running {command} - {e}\n"

    robot.disconnect()
    logbook_log(name=f"{vector.name} completed {commands}", info=response)
    return response


@socketio.on("request_robot_do")
def handle_robot_do(json):
    if "refresh_stats" not in json:
        json["refresh_stats"] = False
    if "send_output" not in json:
        json["send_output"] = True
    if "vector_id" not in json:
        json["vector_id"] = 1

    response = robot_do(json["command"], json["vector_id"])

    if json["send_output"]:
        try:
            emit(
                "server_message",
                {"html": response, "refresh_stats": json["refresh_stats"]},
            )
        except TypeError:
            emit(
                "server_message",
                {
                    "html": f"ERROR! {response.__class__.__name__}",
                    "classes": "theme-warning",
                },
            )


def logbook_log(name, info=None):
    log = Logbook()
    log.name = name
    log.info = info
    log.dt = datetime.now()
    db.session.add(log)
    db.session.commit()

    emit("new_logbook_item", row2dict(log))
