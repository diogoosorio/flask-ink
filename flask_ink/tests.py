#!/usr/env/python
# -*- coding: utf-8 -*-

import unittest, flask, assets, ink

class LocalAssetsTestCase(unittest.TestCase):
    def setUp(self):
        self.instance = assets.LocalAssets()
        self.app = flask.Flask(__name__)

    def test_asset_url(self):
        with self.app.test_request_context('/page'):
            expected = '/static/ink/ink.css'
            actual = self.instance.asset_url('ink.css')
            self.assertEquals(expected, actual)

class ExternalLocationTestCase(unittest.TestCase):

    def setUp(self):
        self.external_location = assets.ExternalLocation('https://code.jquery.com/')

    def test_minified_filename(self):
        filename = 'afile.with.dots.js'
        self.assertEquals('afile.with.dots.min.js', self.external_location.minified_filename(filename))

        filename = 'afile_with_underscores.css'
        self.assertEquals('afile_with_underscores.min.css', self.external_location.minified_filename(filename))

    def test_compile_baseurl(self):
        self.external_location.tokens['custom_token'] = 'custom_value'
        self.external_location.tokens['test_token'] = 'ink_test'
        self.external_location.url_pattern = '{base_url}/{custom_token}?test_token={test_token}'

        expected_url = 'https://code.jquery.com/custom_value?test_token=ink_test'
        actual_url = self.external_location.compile_baseurl()
        self.assertEquals(expected_url, actual_url)

    def test_compile_baseurl_with_invalid_tokens(self):
        # Only the base_url and version tokens are available by default
        self.external_location.url_pattern = '{base_url}/{invalid_token}'

        with self.assertRaises(RuntimeError):
            self.external_location.compile_baseurl()

    def test_asset_url_minified_versioned(self):
        instance = assets.ExternalLocation('cdn.ink.sapo.pt')
        filename = 'demo.css'
        version = ink.__version__

        expected_url = '//cdn.ink.sapo.pt/demo.min.css?v='+version
        actual_url = instance.asset_url(filename, True, version)

        self.assertEquals(expected_url, actual_url)

class SapoCDNTestCase(unittest.TestCase):

    def setUp(self):
        self.instance = assets.SapoCDN()

    def test_minified_filename(self):
        self.assertEquals('development-min.css', self.instance.minified_filename('development.css'))
        self.assertEquals('development.min.js', self.instance.minified_filename('development.js'))

    def test_asset_url(self):
        expected_url = '//cdn.ink.sapo.pt/1.0/application-min.css?v=1.0'
        actual_url = self.instance.asset_url('application.css', True, '1.0')

        self.assertEquals(expected_url, actual_url)

if __name__ == '__main__':
    unittest.main()
