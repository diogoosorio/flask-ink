#!/usr/env/python
# -*- coding: utf-8 -*-

from flask import g, Blueprint, url_for

__version__ = '2.2.1'

class AssetLocation(object):
    def get_url_for(self, filename):
        raise NotImplementedError


class LocalAssets(AssetLocation):
    def __init__(self, directory='static'):
        self.directory = directory

    def get_url_for(self, filename):
        filename = "ink/{0}".format(filename)
        return url_for(self.directory, filename=filename)


class SapoCDN(AssetLocation):
    def __init__(self, ink_version = None, base_url='//cdn.ink.sapo.pt'):
        self.ink_version = __version__ if ink_version is None else ink_version
        self.base_url = base_url.strip('/')

    def get_url_for(self, filename):
        return "//{url}/{version}/{filename}".format(url=self.base_url, version=self.ink_version, filename=filename)


class AssetManager(object):
    def __init__(self, location_map={}, minified=False, asset_version=None):
        self.location_map = location_map
        self.minified = minified
        self.asset_version=asset_version

    def load(self, filename, location='sapo'):
        location_instance = self.get_location_by_name(location)
        filename = filename.strip('/')

        if self.minified:
            filename = self.get_minified_name(filename)

        return location_instance.get_url_for(filename)

    def get_location_by_name(self, name):
        if name in self.location_map:
            return self.location_map[name]

        raise ValueError("Unkown location instance {location_name}.".format(location_name=name))

    def register_location(self, name, location):
        self.location_map[name] = location


class Ink(object):
    def __init__(self, app):
        self.app = app
        self.init_app()

    def init_app(self):
        self.app.config.setdefault('INK_MINIFIED_ASSETS', False);
        self.app.config.setdefault('INK_ASSET_VERSION', __version__)

        minified_assets = self.app.config['INK_MINIFIED_ASSETS']
        asset_version = self.app.config['INK_ASSET_VERSION']

        self.assets = AssetManager(minified=minified_assets, asset_version=asset_version)
        self.make_default_asset_locations()

        blueprint = Blueprint(
            'ink',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=self.app.static_url_path+'/ink')

        self.app.register_blueprint(blueprint)
        self.app.jinja_env.globals.update(ink_load_asset=self.assets.load)

    def make_default_asset_locations(self):
        sapo = SapoCDN()
        local = LocalAssets()

        self.assets.register_location('sapo', sapo)
        self.assets.register_location('local', local)
