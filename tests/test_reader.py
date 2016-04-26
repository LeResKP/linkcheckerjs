#!/usr/bin/env python

import os
import subprocess
import time
import copy

from linkcheckerjs import thread

from unittest import TestCase

import linkcheckerjs.reader as reader


page = {
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
             'http://localhost:8080/unexisting']
}

pages = {
    'http://localhost:8080/': page,
    'http://localhost:8080/page1.html': {
        'checker': 'phantomjs',
        'url': u'http://localhost:8080/',
        'redirect_url': None,
        'parent_url': None,
        'status': u'OK',
        'status_code': 200,
        'resources': [],
        'urls': [],
    },
    'http://localhost:8080/unexisting': {
        'checker': 'phantomjs',
        'url': u'http://localhost:8080/unexisting',
        'redirect_url': None,
        'parent_url': u'http://localhost:8080/',
        'status': u'Not Found',
        'status_code': 404,
        'resources': [],
        'urls': [],
    },
}


class TestElement(TestCase):

    def test__get_display_level(self):
        el = reader.Element({'status_code': 500})
        res = el._get_display_level()
        self.assertEqual(res, reader.ERROR)

        el = reader.Element({'status_code': 302})
        res = el._get_display_level()
        self.assertEqual(res, reader.INFO)

    def test_check_display_level(self):
        el = reader.Element({'status_code': 500})
        res = el.check_display_level(reader.WARNING)
        self.assertEqual(res, True)

        el = reader.Element({'status_code': 302})
        res = el.check_display_level(reader.WARNING)
        self.assertEqual(res, False)

    def test_short_display(self):
        el = reader.Element(page)
        res = el.short_display(reader.INFO)
        self.assertTrue('200 OK' in res)
        self.assertFalse('404 Not Found' in res)
        self.assertFalse('resources' in res)


class TestResource(TestCase):

    def test___init__(self):
        resource = {
            'checker': 'phantomjs',
            'url': u'http://localhost:8080/static/css/style.css',
            'redirect_url': None,
            'parent_url': u'http://localhost:8080/',
            'status': u'OK',
            'status_code': 200
        }
        rs = reader.Resource(resource)
        self.assertEqual(rs.display_level, reader.DEBUG)

        # Not secure resource
        resource = {
            'checker': 'phantomjs',
            'url': u'http://localhost:8080/static/css/style.css',
            'redirect_url': None,
            'parent_url': u'https://localhost:8080/',
            'status': u'OK',
            'status_code': 200
        }
        rs = reader.Resource(resource)
        self.assertEqual(rs.display_level, reader.ERROR)

        resource = {
            'checker': 'phantomjs',
            'url': u'//localhost:8080/static/css/style.css',
            'redirect_url': None,
            'parent_url': u'https://localhost:8080/',
            'status': u'OK',
            'status_code': 200
        }
        rs = reader.Resource(resource)
        self.assertEqual(rs.display_level, reader.DEBUG)


class TestPage(TestCase):

    def test___init__(self):
        page_objs = []
        p = reader.Page(page, page_objs)
        self.assertEqual(len(p.resource_objs), 2)

    def test_display(self):
        dic = {}
        for url, p in pages.items():
            dic[url] = reader.Page(p, dic)

        p = reader.Page(page, dic)
        res = p.display(reader.DEBUG)
        self.assertTrue('200 OK' in res)
        self.assertTrue('404 Not Found' in res)
        self.assertTrue('Resource' in res)
        self.assertTrue('Links' in res)
