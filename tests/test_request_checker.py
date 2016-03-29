#!/usr/bin/env python

import os
import subprocess
# import requests
import time

from unittest import TestCase

from linkcheckerjs.checker import requests_checker


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
        res = requests_checker('http://localhost:8080')
        expected = [{
            'checker': 'requests',
            'url': u'http://localhost:8080/',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
        }]
        self.assertEqual(res, expected)

    def test_ssl_error(self):
        res = requests_checker('https://localhost:8081')
        expected = [{
            'checker': 'requests',
            'url': u'https://localhost:8081/',
            'redirect_url': None,
            'parent_url': None,
            'status': None,
            'status_code': None}]
        self.assertEqual(res, expected)

    def test_200_ok_ignore_ssl(self):
        res = requests_checker('https://localhost:8081',
                               ignore_ssl_errors=True)
        expected = [{
            'checker': 'requests',
            'url': u'https://localhost:8081/',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
        }]
        self.assertEqual(res, expected)

    def test_301_redirect(self):
        res = requests_checker('http://localhost:8080/redirect-301')
        expected = [
            {
                'checker': 'requests',
                'url': u'http://localhost:8080/redirect-301',
                'redirect_url': u'http://localhost:8080',
                'parent_url': None,
                'status': u'Moved Permanently',
                'status_code': 301},
            {
                'checker': 'requests',
                'url': u'http://localhost:8080/',
                'redirect_url': None,
                'parent_url': u'http://localhost:8080/redirect-301',
                'status': u'OK',
                'status_code': 200,
            }]
        self.assertEqual(res, expected)

    def test_302_redirect(self):
        res = requests_checker('http://localhost:8080/redirect-302')
        expected = [
            {
                'checker': 'requests',
                'url': u'http://localhost:8080/redirect-302',
                'redirect_url': u'http://localhost:8080',
                'parent_url': None,
                'status': u'Moved Temporarily',
                'status_code': 302},
            {
                'checker': 'requests',
                'redirect_url': None,
                'parent_url': u'http://localhost:8080/redirect-302',
                'status': u'OK',
                'status_code': 200,
                'url': u'http://localhost:8080/',
            }
        ]
        self.assertEqual(res, expected)

    def test_page1(self):
        res = requests_checker('http://localhost:8080/page1.html')
        expected = [{
            'checker': 'requests',
            'url': u'http://localhost:8080/page1.html',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
        }]
        self.assertEqual(res, expected)

    def test_page2(self):
        res = requests_checker('http://localhost:8080/page2.html')
        expected = [{
            'checker': 'requests',
            'url': u'http://localhost:8080/page2.html',
            'redirect_url': None,
            'parent_url': None,
            'status': u'OK',
            'status_code': 200,
        }]
        self.assertEqual(res, expected)

    def test_page3(self):
        res = requests_checker('http://localhost:8080/page3.html')
        expected = [{
            'checker': 'requests',
            'url': 'http://localhost:8080/page3.html',
            'redirect_url': None,
            'parent_url': None,
            'status': 'OK',
            'status_code': 200,
        }]
        self.assertEqual(res, expected)

    def test_unexisting(self):
        res = requests_checker('http://localhost:8080/unexisting.html')
        expected = [{
            'checker': 'requests',
            "url": "http://localhost:8080/unexisting.html",
            "redirect_url": None,
            "parent_url": None,
            "status_code": 404,
            "status": "Not Found",
        }]
        self.assertEqual(res, expected)
