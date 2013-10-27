#!/usr/env/python
# -*- coding: utf-8 -*-

from Flask import g

__version__ = '2.2.1'

class AssetLocation(object):
    def get_url_for(self, filename):
        raise NotImplementedError


class LocalAssets(AssetLocation):
    def __init__(self, directory='static'):
        self.directory = directory

    def get_url_for(self, filename):
        return url_for(self.directory, filename=filename)


class SapoCDN(AssetLocation):
    def __init__(self, ink_version = None, base_url='//cdn.ink.sapo.pt'):
        self.ink_version = __version__ if ink_version is None else ink_version
        self.base_url = base_url.strip('/')

    def get_url_for(self, filename):
        return "//{url}/{version}/{filename}".format(url=self.base_url, version=self.ink_version, filename=filename)


class AssetManager(object):
    def __init__(self, location_map={}, minified=False):
        self.location_map = location_map
        self.minified = minified

    def load_static_asset(self, filename, location='sapo'):
        location_instance = self.get_location_by_name(location)
        filename = filename.strip('/')

        if self.minified:
            filename = self.get_minified_name(filename)

        return location_instance.get_url_for(filename)

    def get_location_by_name(self, name):
        if key in self.location_map:
            return self.location_map[key]

        raise ValueError("Unkown location instance {location_name}.".format(location_name=name))

    def register_location(self, name, location):
        self.location_map[name] = location


class Ink(object):
    def __init__(self, app):
        self.app = app
        self.init_app()

    def init_app(self):
        key_minified_assets = 'INK_MINIFIED_ASSETS'
        minified_assets = self.app.config[key_minified_assets] if key_minified_assets else False

        self.assets = AssetManager(minified=minfied_assets)
        self.make_default_asset_locations()

        g.ink = self

    def make_default_asset_locations(self):
        sapo = SapoCDN()
        local = LocalAssets()

        self.assets.register_location('sapo', sapo)
        self.assets.register_location('local', local)
