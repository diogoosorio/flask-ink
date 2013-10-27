#!/usr/env/python
# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.appconfig import AppConfig
from sapo_ink import Ink

def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)

    Ink(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    create_app().run(debug=True)
