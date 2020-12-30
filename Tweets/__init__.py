from flask import Flask, app

from config import app_config


def create_app(config_name):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(app_config[config_name])

    return app
