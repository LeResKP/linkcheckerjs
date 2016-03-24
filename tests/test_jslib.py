#!/usr/bin/env python

import os
import subprocess
# import requests
import time

from unittest import TestCase

from linkcheckerjs.checker import phantomjs_checker


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


class TestJSLib(TestCase):

    def test_200_ok(self):
        res = phantomjs_checker('http://localhost:8080')
        expected = [{
            'checker': 'phantomjs',
            'url': u'http://localhost:8080/',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': 'phantomjs',
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
        self.assertEqual(res, expected)

    def test_ssl_error(self):
        res = phantomjs_checker('https://localhost:8081')
        expected = [{
            'checker': 'phantomjs',
            'url': u'https://localhost:8081/',
            'redirect_url': None,
            'parent_url': None,
            'status': None,
            'status_code': None,
            'resources': [],
            'urls': []}]
        self.assertEqual(res, expected)

    def test_200_ok_ignore_ssl(self):
        res = phantomjs_checker('https://localhost:8081',
                                ignore_ssl_errors=True)
        expected = [{
            'checker': 'phantomjs',
            'url': u'https://localhost:8081/',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': 'phantomjs',
                 'url': u'https://localhost:8081/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': u'https://localhost:8081/',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': 'phantomjs',
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
        self.assertEqual(res, expected)

    def test_301_redirect(self):
        res = phantomjs_checker('http://localhost:8080/redirect-301')
        expected = [
            {
                'checker': 'phantomjs',
                'url': u'http://localhost:8080/redirect-301',
                'redirect_url': u'http://localhost:8080',
                'parent_url': None,
                'status': u'Moved Permanently',
                'status_code': 301},
            {
                'checker': 'phantomjs',
                'url': u'http://localhost:8080/',
                'redirect_url': None,
                'parent_url': u'http://localhost:8080/redirect-301',
                'status': u'OK',
                'status_code': 200,
                'resources': [
                    {'checker': 'phantomjs',
                     'parent_url': u'http://localhost:8080/',
                     'redirect_url': None,
                     'status': u'OK',
                     'status_code': 200,
                     'url': u'http://localhost:8080/static/css/style.css'},
                    {'checker': 'phantomjs',
                     'parent_url': u'http://localhost:8080/',
                     'redirect_url': None,
                     'status': u'Not Found',
                     'status_code': 404,
                     'url': u'http://localhost:8080/static/css/unexisting.css'}
                ],
                'urls': ['http://localhost:8080/page1.html',
                         'http://localhost:8080/page2.html',
                         'http://localhost:8080/unexisting']}]

        self.assertEqual(res, expected)

    def test_302_redirect(self):
        res = phantomjs_checker('http://localhost:8080/redirect-302')
        expected = [
            {
                'checker': 'phantomjs',
                'url': u'http://localhost:8080/redirect-302',
                'redirect_url': u'http://localhost:8080',
                'parent_url': None,
                'status': u'Moved Temporarily',
                'status_code': 302},
            {
                'checker': 'phantomjs',
                'redirect_url': None,
                'parent_url': u'http://localhost:8080/redirect-302',
                'status': u'OK',
                'status_code': 200,
                'url': u'http://localhost:8080/',
                'resources': [
                    {'checker': 'phantomjs',
                     'parent_url': u'http://localhost:8080/',
                     'redirect_url': None,
                     'status': u'OK',
                     'status_code': 200,
                     'url': u'http://localhost:8080/static/css/style.css'},
                    {'checker': 'phantomjs',
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
        self.assertEqual(res, expected)

    def test_page1(self):
        res = phantomjs_checker('http://localhost:8080/page1.html')
        expected = [{
            'checker': 'phantomjs',
            'url': u'http://localhost:8080/page1.html',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page1.html',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/images/unexisting.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page1.html',
                 'status': u'Not Found',
                 'status_code': 404},
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/images/image1.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page1.html',
                 'status': u'OK',
                 'status_code': 200},
            ],
            u'urls': []}]
        self.assertEqual(res, expected)

    def test_page2(self):
        res = phantomjs_checker('http://localhost:8080/page2.html')
        expected = [{
            'checker': 'phantomjs',
            'url': u'http://localhost:8080/page2.html',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
            'resources': [
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/redirect-static-301/css/style.css',
                 'redirect_url': u'http://localhost:8080/static/css/style.css',
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'Moved Permanently',
                 'status_code': 301},
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/redirect-static-301/images/unexisting.png',
                 'redirect_url': u'http://localhost:8080/static/images/unexisting.png',
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'Moved Permanently',
                 'status_code': 301},
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/redirect-static-302/images/image1.png',
                 'redirect_url': u'http://localhost:8080/static/images/image1.png',
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'Moved Temporarily',
                 'status_code': 302},
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/images/unexisting.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'Not Found',
                 'status_code': 404},
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/images/image1.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page2.html',
                 'status': u'OK',
                 'status_code': 200}],
            u'urls': []}]

        res[0]['resources'].sort()
        expected[0]['resources'].sort()
        self.assertEqual(res, expected)

    def test_page3(self):
        res = phantomjs_checker('http://localhost:8080/page3.html')
        expected = [{
            'checker': 'phantomjs',
            'url': 'http://localhost:8080/page3.html',
            'redirect_url': None,
            'parent_url': None,
            'status': 'OK',
            'status_code': 200,
            'resources': [
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/css/style.css',
                 'redirect_url': None,
                 'parent_url': 'http://localhost:8080/page3.html',
                 'status': u'OK',
                 'status_code': 200},
                {'checker': 'phantomjs',
                 'url': u'http://localhost:8080/static/images/image1.png',
                 'redirect_url': None,
                 'parent_url': u'http://localhost:8080/page3.html',
                 'status': 'OK',
                 'status_code': 200},
                {'checker': 'phantomjs',
                 'url': 'http://localhost:8080/static/images/unexisting.png',
                 'redirect_url': None,
                 'parent_url': 'http://localhost:8080/page3.html',
                 'status': 'Not Found',
                 'status_code': 404}],
            u'urls': []
        }]

        self.assertEqual(res, expected)

    def test_unexisting(self):
        res = phantomjs_checker('http://localhost:8080/unexisting.html')
        expected = [{
            'checker': 'phantomjs',
            "url": "http://localhost:8080/unexisting.html",
            "redirect_url": None,
            "parent_url": None,
            "status_code": 404,
            "status": "Not Found",
            "resources": [],
            "urls": [],
        }]
        self.assertEqual(res, expected)
