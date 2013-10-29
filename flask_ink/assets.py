#!/usr/env/python
# -*- coding: utf-8 -*-

import re

class AssetLocation(object):
    def asset_url(self, filename, minified=False, version=None):
        raise NotImplementedError

class LocalAssets(AssetLocation):
    def __init__(self, directory='static'):
        self.directory = directory

    def asset_url(self, filename):
        filename = "ink/{0}".format(filename)
        return url_for(self.directory, filename=filename)

class ExternalLocation(AssetLocation):
    def __init__(self, base_url, url_pattern="//{base_url}/{filename}"):
        self.base_url = base_url.rstrip('/')
        self.url_pattern = url_pattern

    def minified_filename(self, filename):
        return '%s.min.%s' % tuple(filename.rsplit('.', 1))

    def compile_baseurl(self, version=None):
        regex = re.compile('\{(\w+)\}')
        symbols = regex.findall(self.url_pattern)
        known_symbols = ['version']
        unknown_symbols = set(symbols) - set(known_symbols)

        if len(unknown_symbols):
            raise RuntimeError("Unknown symbols on your url_pattern: {}".format(unknown_symbols))

        return self.base_url.format(version=version)

    def asset_url(self, filename, minified=False, version=None):
        if minified:
            filename = self.minified_filename(filename)

        base_url = self.compile_baseurl(version)
        base_url += '/'+filename

        return url


class SapoCDN(ExternalLocation):
    def minified_filename(self, filename):
        filename_parts = filename.rsplit('.', 1)
        extension = filename_parts[1]

        pattern = '%s-min.%s' if filename_parts[1] == 'css' else '%s.min.%s'
        return pattern % tuple(filename_parts)


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

