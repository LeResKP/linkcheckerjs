#!/usr/bin/env python

import os
import subprocess
import time
import copy

from linkcheckerjs import thread

from unittest import TestCase

import linkcheckerjs.run as run


class TestLinkcheckerjs(TestCase):

    @classmethod
    def setUpClass(cls):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        server_js = os.path.join(dir_path, 'http', 'server.js')
        cls.process = subprocess.Popen(['node', server_js])
        time.sleep(.1)

    @classmethod
    def tearDownClass(cls):
        cls.process.kill()

    def setUp(self):
        super(TestLinkcheckerjs, self).setUp()
        self.pool = thread.ThreadPool(1)
        self.pool.stop_threads()

    def tearDown(self):
        self.pool.stop_threads()
        super(TestLinkcheckerjs, self).tearDown()

    def test_check(self):
        linkchecker = run.Linkchecker(self.pool)
        linkchecker.check('http://localhost:8080')
        self.assertEqual(len(linkchecker.results), 4)

    def test_quick_check(self):
        linkchecker = run.Linkchecker(self.pool)
        linkchecker.quick_check('http://localhost:8080')
        self.assertEqual(len(linkchecker.results), 1)

    def test_schedule(self):
        url = 'http://localhost:8080/'
        linkchecker = run.Linkchecker(self.pool)
        linkchecker.schedule(url)
        self.assertEqual(linkchecker.results[url], None)
        self.assertEqual(len(self.pool._tasks), 1)
        self.assertEqual(self.pool._tasks[0][0].__name__, 'quick_check')

        linkchecker.valid_domains = ['localhost']
        linkchecker.schedule(url)
        self.assertEqual(linkchecker.results[url], None)
        self.assertEqual(len(self.pool._tasks), 2)
        self.assertEqual(self.pool._tasks[1][0].__name__, 'check')

    def test_filter_urls(self):
        urls = [
            'http://localhost:8080',
            'mailto:something',
            'data:something',
        ]

        linkchecker = run.Linkchecker(self.pool)
        res = linkchecker.filter_urls(urls)
        expected = [
            'http://localhost:8080',
        ]
        self.assertEqual(list(res), expected)

    def test_filter_ignore_urls_patterns(self):
        urls = [
            'http://localhost:8080',
            'http://localhost:8080/ignored',
        ]
        linkchecker = run.Linkchecker(self.pool)
        res = linkchecker.filter_ignore_urls_patterns(urls)
        self.assertEqual(list(res), urls)

        linkchecker = run.Linkchecker(self.pool,
                                      ignore_url_patterns=['ignored'])
        res = linkchecker.filter_ignore_urls_patterns(urls)
        self.assertEqual(list(res), ['http://localhost:8080'])

    def test_feed_result(self):
        url = 'http://localhost:8080'
        result = {
            'urls': ['http://localhost:8080/page1']
        }
        new_depth = 0
        linkchecker = run.Linkchecker(self.pool)
        linkchecker.feed_result(url, result, new_depth)
        self.assertEqual(len(self.pool._tasks), 1)
        self.assertEqual(linkchecker.results.keys(), result['urls'])

        # Don't add twice the same url
        linkchecker.feed_result(url, result, new_depth)
        self.assertEqual(len(self.pool._tasks), 1)
