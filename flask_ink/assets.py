#!/usr/env/python
# -*- coding: utf-8 -*-

import re
import flask
import ink

class AssetLocation(object):
    def asset_url(self, filename, minified=False, version=None):
        raise NotImplementedError

    def minified_filename(self, filename):
        return '%s.min.%s' % tuple(filename.rsplit('.', 1))

    def versioned_filename(self, filename, version):
        if type(version) is bool:
            version = __version__

        return filename+'?v='+version


class LocalAssets(AssetLocation):
    def __init__(self, directory='static'):
        self.directory = directory

    def asset_url(self, filename, minified=False, version=None):
        filename = self.minified_filename(filename) if minified else filename
        filename = "ink/{0}".format(filename)

        params = {'filename': filename}

        if version:
            params['v'] = version

        return flask.url_for(self.directory, **params)


class ExternalLocation(AssetLocation):
    def __init__(self, base_url, url_pattern="//{base_url}", tokens = {}):
        self.base_url = base_url.rstrip('/')
        self.url_pattern = url_pattern.rstrip('/')

        tokens['base_url'] = self.base_url
        self.tokens = tokens

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
        filename = self.minified_filename(filename) if minified else filename
        filename = self.versioned_filename(filename, version) if version else filename

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
        self.default_location = default_location
        self.append_querystring = append_querystring

        # Make sure we have a valid default location, as the get_location_by_name method
        # raises an error if it isn't registered
        if self.default_location is not None:
            self.get_location_by_name(self.default_location)

    def load(self, filename, location=None):
        location = location or self.default_location
        location_instance = self.get_location_by_name(location)

        filename = filename.strip('/')
        return location_instance.asset_url(filename, self.minified, self.asset_version)

    def get_location_by_name(self, name):
        if name in self.location_map:
            return self.location_map[name]

        name = '' if type(name) != str else name
        raise UnknownAssetLocationError("Unkown location instance "+name)


    def register_location(self, name, location):
        self.location_map[name] = location


class UnknownAssetLocationError(RuntimeError):
    pass
