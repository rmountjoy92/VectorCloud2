#!/usr/bin/env python3

from vectorcloud import app, socketio
from vectorcloud.main.utils import database_init

if __name__ == "__main__":
    database_init()
    socketio.run(app)
