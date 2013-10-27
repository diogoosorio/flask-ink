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
    def __init__(
        self, location_map={}, minified=False, asset_version=None,
        default_location=None, append_querystring=False
        ):

        self.location_map = location_map
        self.minified = minified
        self.asset_version = asset_version
        self.default_location = default_location or 'sapo'
        self.append_querystring = append_querystring

    def load(self, filename, location=None):
        location = location or self.default_location
        location_instance = self.get_location_by_name(location)

        filename = filename.strip('/')

        if self.minified:
            filename = '%s.min.%s' % tuple(filename.rsplit('.', 1))

        asset_location = location_instance.get_url_for(filename)

        if self.append_querystring:
            asset_location = '{0}?v={1}'.format(asset_location, self.asset_version)

        return asset_location

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
        self.app.config.setdefault('INK_ASSET_MINIFY', False);
        self.app.config.setdefault('INK_ASSET_VERSION', __version__)
        self.app.config.setdefault('INK_ASSET_DEFAULT_LOCATION', 'sapo')
        self.app.config.setdefault('INK_ASSET_APPEND_VERSION_QUERYSTRING', False)

        minified_assets = self.app.config['INK_ASSET_MINIFY']
        asset_version = self.app.config['INK_ASSET_VERSION']
        asset_location = self.app.config['INK_ASSET_DEFAULT_LOCATION']
        append_version = self.app.config['INK_ASSET_APPEND_VERSION_QUERYSTRING']

        self.assets = AssetManager(
            minified=minified_assets, asset_version=asset_version,
            default_location=asset_location, append_querystring=append_version)

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
