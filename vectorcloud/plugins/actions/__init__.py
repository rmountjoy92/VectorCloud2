import anki_vector


def do_actions(actions, vector):

    with anki_vector.Robot(vector.serial) as robot:
        for action in actions:
            if action["action"] == "say":
                robot.behavior.say_text(action["text_to_say"])

            elif action["action"] == "undock":
                robot.behavior.drive_off_charger()

            elif action["action"] == "dock":
                robot.behavior.drive_on_charger()

    return "Commands completed"
