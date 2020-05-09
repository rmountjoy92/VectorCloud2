#!/usr/bin/env python3

from vectorcloud import app, socketio

if __name__ == "__main__":
    socketio.run(app=app, debug=True, use_reloader=True, host="0.0.0.0", port=5000)
