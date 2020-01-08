import os
from pathlib import Path


# root path of the application
def get_root_folder():
    curr_folder = os.path.dirname(__file__)
    root_folder = Path(curr_folder).parent
    return root_folder


root_folder = get_root_folder()

elm_folder = os.path.join(root_folder, "vectorcloud")

static_folder = os.path.join(elm_folder, "static")

images_folder = os.path.join(static_folder, "images")

cache_folder = os.path.join(static_folder, "cache")

user_images_folder = os.path.join(images_folder, "user")

home_folder = Path.home()

sdk_config_file = os.path.join(home_folder, ".anki_vector", "sdk_config.ini")
