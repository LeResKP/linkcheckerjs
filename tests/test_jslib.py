#!/usr/bin/env python

import os
import subprocess
# import requests
import time

from unittest import TestCase

from linkcheckerjs.checker import phantomjs_checker


import pprint


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
        res = phantomjs_checker('http://localhost:8080', 'localhost')
        pprint.pprint(res)
        expected = {
            u'page': {
                u'redirect_url': None,
                u'response_url': u'http://localhost:8080/',
                u'status': u'OK',
                u'status_code': 200,
                u'url': u'http://localhost:8080'},
            u'resources': [
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/css/unexisting.css',
                 u'status': u'Not Found',
                 u'status_code': 404,
                 u'url': u'http://localhost:8080'},
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/css/style.css',
                 u'status': u'OK',
                 u'status_code': 200,
                 u'url': u'http://localhost:8080'}
            ],
            u'urls': [u'http://localhost:8080/page1',
                      u'http://localhost:8080/page2',
                      u'http://localhost:8080/unexisting']
        }
        self.assertEqual(res, expected)

    def test_301_redirect(self):
        res = phantomjs_checker('http://localhost:8080/redirect-301', 'localhost')
        pprint.pprint(res)
        expected = {
            u'page': {
                u'redirect_url': u'http://localhost:8080',
                u'response_url': u'http://localhost:8080/redirect-301',
                u'status': u'Moved Permanently',
                u'status_code': 301,
                u'url': u'http://localhost:8080/redirect-301'},
            u'resources': [],
            u'urls': [u'http://localhost:8080']}
        self.assertEqual(res, expected)

    def test_302_redirect(self):
        res = phantomjs_checker('http://localhost:8080/redirect-302', 'localhost')
        pprint.pprint(res)
        expected = {
            u'page': {
                u'redirect_url': u'http://localhost:8080',
                u'response_url': u'http://localhost:8080/redirect-302',
                u'status': u'Moved Temporarily',
                u'status_code': 302,
                u'url': u'http://localhost:8080/redirect-302'},
            u'resources': [],
            u'urls': [u'http://localhost:8080']}
        self.assertEqual(res, expected)

    def test_page1(self):
        res = phantomjs_checker('http://localhost:8080/page1.html', 'localhost')
        pprint.pprint(res)
        expected = {
            u'page': {
                u'redirect_url': None,
                u'response_url': u'http://localhost:8080/page1.html',
                u'status': u'OK',
                u'status_code': 200,
                u'url': u'http://localhost:8080/page1.html'},
            u'resources': [
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/images/unexisting.png',
                 u'status': u'Not Found',
                 u'status_code': 404,
                 u'url': u'http://localhost:8080/page1.html'},
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/images/image1.png',
                 u'status': u'OK',
                 u'status_code': 200,
                 u'url': u'http://localhost:8080/page1.html'},
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/css/style.css',
                 u'status': u'OK',
                 u'status_code': 200,
                 u'url': u'http://localhost:8080/page1.html'}],
            u'urls': []}
        self.assertEqual(res, expected)

    def test_page2(self):
        res = phantomjs_checker('http://localhost:8080/page2.html', 'localhost')
        pprint.pprint(res)
        expected = {
            u'page': {
                u'redirect_url': None,
                u'response_url': u'http://localhost:8080/page2.html',
                u'status': u'OK',
                u'status_code': 200,
                u'url': u'http://localhost:8080/page2.html'},
            u'resources': [
                {u'redirect_url': u'http://localhost:8080/static/css/style.css',
                 u'response_url': u'http://localhost:8080/redirect-static-301/css/style.css',
                 u'status': u'Moved Permanently',
                 u'status_code': 301,
                 u'url': u'http://localhost:8080/page2.html'},
                {u'redirect_url': u'http://localhost:8080/static/images/unexisting.png',
                 u'response_url': u'http://localhost:8080/redirect-static-301/images/unexisting.png',
                 u'status': u'Moved Permanently',
                 u'status_code': 301,
                 u'url': u'http://localhost:8080/page2.html'},
                {u'redirect_url': u'http://localhost:8080/static/images/image1.png',
                 u'response_url': u'http://localhost:8080/redirect-static-302/images/image1.png',
                 u'status': u'Moved Temporarily',
                 u'status_code': 302,
                 u'url': u'http://localhost:8080/page2.html'},
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/images/unexisting.png',
                 u'status': u'Not Found',
                 u'status_code': 404,
                 u'url': u'http://localhost:8080/page2.html'},
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/css/style.css',
                 u'status': u'OK',
                 u'status_code': 200,
                 u'url': u'http://localhost:8080/page2.html'},
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/images/image1.png',
                 u'status': u'OK',
                 u'status_code': 200,
                 u'url': u'http://localhost:8080/page2.html'}],
            u'urls': []}

        self.assertEqual(res, expected)

    def test_page3(self):
        res = phantomjs_checker('http://localhost:8080/page3.html', 'localhost')
        pprint.pprint(res)
        expected = {
            u'page': {u'redirect_url': None,
                      u'response_url': u'http://localhost:8080/page3.html',
                      u'status': u'OK',
                      u'status_code': 200,
                      u'url': u'http://localhost:8080/page3.html'},
            u'resources': [
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/css/style.css',
                 u'status': u'OK',
                 u'status_code': 200,
                 u'url': u'http://localhost:8080/page3.html'},
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/images/unexisting.png',
                 u'status': u'Not Found',
                 u'status_code': 404,
                 u'url': u'http://localhost:8080/page3.html'},
                {u'redirect_url': None,
                 u'response_url': u'http://localhost:8080/static/images/image1.png',
                 u'status': u'OK',
                 u'status_code': 200,
                 u'url': u'http://localhost:8080/page3.html'}],
            u'urls': []}

        self.assertEqual(res, expected)
