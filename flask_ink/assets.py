#!/usr/env/python
# -*- coding: utf-8 -*-

import re, flask, ink

class AssetLocation(object):
    def asset_url(self, filename, minified=False, version=None):
        raise NotImplementedError

class LocalAssets(AssetLocation):
    def __init__(self, directory='static'):
        self.directory = directory

    def asset_url(self, filename):
        filename = "ink/{0}".format(filename)
        return flask.url_for(self.directory, filename=filename)


class ExternalLocation(AssetLocation):
    def __init__(self, base_url, url_pattern="//{base_url}", tokens = {}):
        self.base_url = base_url.rstrip('/')
        self.url_pattern = url_pattern.rstrip('/')

        tokens['base_url'] = self.base_url

        self.tokens = tokens


    def minified_filename(self, filename):
        return '%s.min.%s' % tuple(filename.rsplit('.', 1))


    def compile_baseurl(self, version=None):
        regex = re.compile('\{(\w+)\}')
        tokens = regex.findall(self.url_pattern)
        known_tokens = self.tokens

        version = version or ink.__version__
        known_tokens['version'] = version

        unknown_tokens = set(tokens) - set(known_tokens)

        if len(unknown_tokens):
            raise RuntimeError("Unknown tokens on your url_pattern: {}".format(unknown_tokens))

        return self.url_pattern.format(**known_tokens)


    def asset_url(self, filename, minified=False, version=None):
        if minified:
            filename = self.minified_filename(filename)

        if version and type(version) is bool:
            version = __version__

        if version:
            filename += '?v='+version

        base_url = self.compile_baseurl(version)
        base_url += '/'+filename

        return base_url


class SapoCDN(ExternalLocation):

    def __init__(self, tokens = {}):
        base_url = 'cdn.ink.sapo.pt'
        url_pattern = '//{base_url}/{version}'

        super(SapoCDN, self).__init__(base_url, url_pattern, tokens)

    def minified_filename(self, filename):
        filename_parts = filename.rsplit('.', 1)
        extension = filename_parts[1]

        pattern = '%s-min.%s' if filename_parts[1] == 'css' else '%s.min.%s'
        return pattern % tuple(filename_parts)


class AssetManager(object):
    def __init__(
        self, location_map={}, minified=False, asset_version=None,
        default_location=None, append_querystring=False):

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

