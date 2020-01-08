#!/usr/bin/env python3

from vectorcloud import app, socketio
from vectorcloud.main.utils import database_init

if __name__ == "__main__":
    database_init()
    socketio.run(app=app, debug=True, use_reloader=True, host="0.0.0.0")
