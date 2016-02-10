#!/usr/bin/env python

import threading
from subprocess import Popen, PIPE
from optparse import OptionParser
import json

from . import thread


PHANTOMJS = './node_modules/.bin/phantomjs'


class Linkchecker(object):

    def __init__(self, pool):
        self.pool = pool
        self.checked_urls = set()
        self.queued_urls = set()
        self.__checkLock = threading.Condition(threading.Lock())
        self.depth = 0
        self.res = {}

    def check(self, data):
        cmd = [PHANTOMJS]
        if data['ignore_ssl_errors'] is True:
            cmd += ['--ignore-ssl-errors=yes']
        cmd += ['lib/linkchecker.js']
        if data['log_level'] is not None:
            cmd += ['--log-level=%i' % data['log_level']]
        cmd += [data['url']]

        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = process.communicate()
        try:
            result = json.loads(stdout)
        except:
            pass
        self.store(data['url'], result)
        self.checked_urls.add(data['url'])

    def filter_urls(self, urls):
        self.__checkLock.acquire()
        try:
            urls -= self.checked_urls
            urls -= self.queued_urls
            self.queued_urls |= urls
            return urls
        finally:
            self.__checkLock.release()

    def store(self, url, result):
        links = set(result['links'])
        res = result['res']
        self.res[url] = res
        links = self.filter_urls(links)
        if self.depth < 1:
            self.depth += 1
            for link in links:
                self.pool.add_task(self.check, {
                    'url': link,
                    'ignore_ssl_errors': False,
                    'log_level': None})


def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="Urls list", metavar="FILE")
    parser.add_option("-l", "--log-level", type="int", dest="log_level",
                      help="linkcheckerjs log level")
    parser.add_option("-i", "--ignore-ssl-errors", action="store_true",
                      dest="ignore_ssl_errors",
                      help="Ignore ssl errors for self signed certificate")
    (options, args) = parser.parse_args()

    if options.filename is None and not args:
        raise Exception('Filename required')

    # Create a pool
    pool = thread.ThreadPool(20)

    linkchecker = Linkchecker(pool)
    if options.filename:
        with open(options.filename, 'r') as f:
            for url in f.readlines():
                pool.add_task(linkchecker.check, {
                    'url': url.strip(),
                    'ignore_ssl_errors': options.ignore_ssl_errors,
                    'log_level': options.log_level})
    else:
        for url in args:
            pool.add_task(linkchecker.check, {
                'url': url.strip(),
                'ignore_ssl_errors': options.ignore_ssl_errors,
                'log_level': options.log_level})
    pool.join_all()


if __name__ == "__main__":
    main()
