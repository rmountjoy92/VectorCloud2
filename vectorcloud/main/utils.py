import anki_vector
from flask_socketio import emit
from vectorcloud import config, socketio
from vectorcloud.paths import sdk_config_file

# establishes routes decorated w/ @public_route as accessible while not signed
# in. See login and register routes for usage
def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function


def database_init():
    pass


def vector_connect(behavior_control_level=None):
    args = anki_vector.util.parse_command_args()
    robot = anki_vector.Robot(
        args.serial, behavior_control_level=behavior_control_level
    )
    try:
        robot.connect()
        return robot
    except Exception as e:
        raise e


def get_stats():
    response = {}

    # get robot name and ip from config file
    f = open(sdk_config_file, "r")
    serial = f.readline()
    serial = serial.replace("]", "")
    serial = serial.replace("[", "")
    serial = serial.replace("\n", "")
    f.close()
    config.read(sdk_config_file)
    response["ip"] = config.get(serial, "ip")
    response["name"] = config.get(serial, "name")

    # get results from battery state and version state
    try:
        robot = vector_connect()
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

    return response


@socketio.on("request_stats")
def handle_stats_request():
    response = get_stats()
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
def robot_do(commands, override_output=None):
    args = anki_vector.util.parse_command_args()
    robot = anki_vector.Robot(args.serial)
    try:
        robot.connect()
    except Exception as e:
        return e

    response = ""
    for command in commands.split(","):
        try:
            response = f"{str(eval(command))}\n"
        except Exception as e:
            robot.disconnect()
            return e

    robot.disconnect()

    return response


@socketio.on("request_robot_do")
def handle_robot_do(json):
    response = robot_do(json)
    try:
        emit(
            "server_message", {"html": response},
        )
    except TypeError:
        emit(
            "server_message",
            {
                "html": f"ERROR! {response.__class__.__name__}",
                "classes": "theme-warning",
            },
        )
