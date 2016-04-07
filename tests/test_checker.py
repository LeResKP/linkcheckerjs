#!/usr/bin/env python

import os
import subprocess
import time
import copy

from unittest import TestCase

from linkcheckerjs.checker import (
    phantomjs_checker,
    requests_checker,
    standardize_url)


process = None


def setup_module(module):
    global process
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    server_js = os.path.join(dir_path, 'http', 'server.js')
    process = subprocess.Popen(['node', server_js])
    time.sleep(.1)


def teardown_module(module):
    process.kill()


class BaseTest(object):
    checker_name = None

    def test_200_ok(self):
        url = 'http://localhost:8080'
        expected = [{
            'checker': self.checker_name,
            'url': u'http://localhost:8080/',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/css/unexisting.css',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/',
                 'status': u'Not Found',
                 'status_code': 404},
            ],
            'urls': ['http://localhost:8080/page1.html',
                     'http://localhost:8080/page2.html',
                     'http://localhost:8080/unexisting']
        }]
        self.check(url, expected)

    def test_ssl_error(self):
        url = 'https://localhost:8081'
        expected = [{
            'checker': self.checker_name,
            'url': u'https://localhost:8081/',
            'redirect_url': None,
            'parent_url': None,
            'status': None,
            'status_code': None,
            'resources': [],
            'urls': []}]
        self.check(url, expected)

    def test_200_ok_ignore_ssl(self):
        url = 'https://localhost:8081'
        expected = [{
            'checker': self.checker_name,
            'url': u'https://localhost:8081/',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': self.checker_name,
                 'url': u'https://localhost:8081/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': u'https://localhost:8081/',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': self.checker_name,
                 'url': u'https://localhost:8081/static/css/unexisting.css',
                 'redirect_url': None,
                 'parent_url': u'https://localhost:8081/',
                 'status': u'Not Found',
                 'status_code': 404},
            ],
            'urls': ['https://localhost:8081/page1.html',
                     'https://localhost:8081/page2.html',
                     'https://localhost:8081/unexisting']
        }]
        self.check(url, expected, ignore_ssl_errors=True)

    def test_301_redirect(self):
        url = 'http://localhost:8080/redirect-301'
        expected = [
            {
                'checker': self.checker_name,
                'url': u'http://localhost:8080/redirect-301',
                'redirect_url': u'http://localhost:8080',
                'parent_url': None,
                'status': u'Moved Permanently',
                'status_code': 301},
            {
                'checker': self.checker_name,
                'url': u'http://localhost:8080/',
                'redirect_url': None,
                'parent_url': u'http://localhost:8080/redirect-301',
                'status': u'OK',
                'status_code': 200,
                'resources': [
                    {'checker': self.checker_name,
                     'parent_url': u'http://localhost:8080/',
                     'redirect_url': None,
                     'status': u'OK',
                     'status_code': 200,
                     'url': u'http://localhost:8080/static/css/style.css'},
                    {'checker': self.checker_name,
                     'parent_url': u'http://localhost:8080/',
                     'redirect_url': None,
                     'status': u'Not Found',
                     'status_code': 404,
                     'url': u'http://localhost:8080/static/css/unexisting.css'}
                ],
                'urls': ['http://localhost:8080/page1.html',
                         'http://localhost:8080/page2.html',
                         'http://localhost:8080/unexisting']}]

        self.check(url, expected)

    def test_302_redirect(self):
        url = 'http://localhost:8080/redirect-302'
        expected = [
            {
                'checker': self.checker_name,
                'url': u'http://localhost:8080/redirect-302',
                'redirect_url': u'http://localhost:8080',
                'parent_url': None,
                'status': u'Moved Temporarily',
                'status_code': 302},
            {
                'checker': self.checker_name,
                'redirect_url': None,
                'parent_url': u'http://localhost:8080/redirect-302',
                'status': u'OK',
                'status_code': 200,
                'url': u'http://localhost:8080/',
                'resources': [
                    {'checker': self.checker_name,
                     'parent_url': u'http://localhost:8080/',
                     'redirect_url': None,
                     'status': u'OK',
                     'status_code': 200,
                     'url': u'http://localhost:8080/static/css/style.css'},
                    {'checker': self.checker_name,
                     'parent_url': u'http://localhost:8080/',
                     'redirect_url': None,
                     'status': u'Not Found',
                     'status_code': 404,
                     'url': u'http://localhost:8080/static/css/unexisting.css'}
                ],
                'urls': [
                    'http://localhost:8080/page1.html',
                    'http://localhost:8080/page2.html',
                    'http://localhost:8080/unexisting']}
        ]
        self.check(url, expected)

    def test_page1(self):
        url = 'http://localhost:8080/page1.html'
        expected = [{
            'checker': self.checker_name,
            'url': u'http://localhost:8080/page1.html',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page1.html',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/images/unexisting.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page1.html',
                 'status': u'Not Found',
                 'status_code': 404},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/images/image1.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page1.html',
                 'status': u'OK',
                 'status_code': 200},
            ],
            u'urls': []}]
        self.check(url, expected)

    def test_page2(self):
        url = 'http://localhost:8080/page2.html'
        expected = [{
            'checker': self.checker_name,
            'url': u'http://localhost:8080/page2.html',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/redirect-static-301/css/style.css',
                 'redirect_url': u'http://localhost:8080/static/css/style.css',
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'Moved Permanently',
                 'status_code': 301},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/redirect-static-301/images/unexisting.png',
                 'redirect_url': u'http://localhost:8080/static/images/unexisting.png',
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'Moved Permanently',
                 'status_code': 301},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/redirect-static-302/images/image1.png',
                 'redirect_url': u'http://localhost:8080/static/images/image1.png',
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'Moved Temporarily',
                 'status_code': 302},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/images/unexisting.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'Not Found',
                 'status_code': 404},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/images/image1.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'OK',
                 'status_code': 200}],
            u'urls': []}]
        self.check(url, expected)

    def test_page3(self):
        url = 'http://localhost:8080/page3.html'
        expected = [{
            'checker': self.checker_name,
            'url': 'http://localhost:8080/page3.html',
            'redirect_url': None,
            'parent_url': None,
            'status': 'OK',
            'status_code': 200,
            'resources': [
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': 'http://localhost:8080/page3.html',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/static/images/image1.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page3.html',
                 'status': 'OK',
                 'status_code': 200},
                {'checker': self.checker_name,
                 'url': 'http://localhost:8080/static/images/unexisting.png',
                 'redirect_url': None,
                 'parent_url': 'http://localhost:8080/page3.html',
                 'status': 'Not Found',
                 'status_code': 404}],
            u'urls': []
        }]

        self.check(url, expected)

    def test_unexisting(self):
        url = 'http://localhost:8080/unexisting.html'
        expected = [{
            'checker': self.checker_name,
            "url": "http://localhost:8080/unexisting.html",
            "redirect_url": None,
            "parent_url": None,
            "status_code": 404,
            "status": "Not Found",
            "resources": [],
            "urls": [],
        }]
        self.check(url, expected)

    def test_timeout(self):
        url = 'http://localhost:8080/timeout'
        expected = [{
            'checker': self.checker_name,
            "url": "http://localhost:8080/timeout",
            "redirect_url": None,
            "parent_url": None,
            "status_code": 408,
            "status": "Request Time-out",
            "resources": [],
            "urls": [],
        }]
        self.check(url, expected, timeout=1)
        time.sleep(1.5)

    def test_timeout_resource(self):
        url = 'http://localhost:8080/timeout.html'
        expected = [{
            'checker': self.checker_name,
            'url': u'http://localhost:8080/timeout.html',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': self.checker_name,
                 'url': u'http://localhost:8080/timeout',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/timeout.html',
                 'status': u'Request Time-out',
                 'status_code': 408},
            ],
            u'urls': []}]
        self.maxDiff = None
        self.check(url, expected, timeout=1)
        time.sleep(1.5)


class TestPhantomjsChecker(TestCase, BaseTest):
    checker_name = 'phantomjs'

    def check(self, url, expected, ignore_ssl_errors=False, timeout=None):
        res = phantomjs_checker(url, ignore_ssl_errors=ignore_ssl_errors,
                                timeout=timeout)
        for d in expected:
            if 'resources' in d:
                d['resources'].sort()
        for d in res:
            if 'resources' in d:
                d['resources'].sort()
        self.assertEqual(res, expected)


class TestRequestsChecker(TestCase, BaseTest):
    checker_name = 'requests'

    def check(self, url, expected, ignore_ssl_errors=False, timeout=None):
        expected = copy.deepcopy(expected)
        for d in expected:
            d.pop('resources', None)
            d.pop('urls', None)
        res = requests_checker(url, ignore_ssl_errors=ignore_ssl_errors,
                               timeout=timeout)
        self.assertEqual(res, expected)


class TestUtils(TestCase):

    def test_standardize_url(self):
        url = 'http://www.lereskp.fr'
        res = standardize_url(url)
        expected = 'http://www.lereskp.fr/'
        self.assertEqual(res, expected)

        url = 'http://www.lereskp.fr/'
        res = standardize_url(url)
        expected = 'http://www.lereskp.fr/'
        self.assertEqual(res, expected)

        url = 'http://www.lereskp.fr/page'
        res = standardize_url(url)
        self.assertEqual(res, url)
