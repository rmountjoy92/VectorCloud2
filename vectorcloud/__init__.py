#!/usr/bin/env python3

from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_restful import Api
from flask_avatars import Avatars
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO
from configparser import ConfigParser


app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})
api = Api(app)
avatars = Avatars(app)

app.config["AVATARS_IDENTICON_BG"] = (255, 255, 255)
app.config["SECRET_KEY"] = "66532a62c4048f976e22a39638b6f10e"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# scheduler config
app.config["SCHEDULER_API_ENABLED"] = True
app.config["SCHEDULER_JOBSTORES"] = {
    "default": SQLAlchemyJobStore(url="sqlite:///scheduler.db")
}

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
socketio = SocketIO(app)
config = ConfigParser()

from vectorcloud.main.routes import main
from vectorcloud.user_system.routes import user_system
from vectorcloud.error_pages.routes import error_pages
from vectorcloud import sources

app.register_blueprint(main)
app.register_blueprint(user_system)
app.register_blueprint(error_pages)


from vectorcloud.rest_api.resources import *

api.add_resource(Version, "/api/version")
api.add_resource(RunPlugin, "/api/run")

from vectorcloud.main.utils import start_plugins, handle_run_plugin

start_plugins()
