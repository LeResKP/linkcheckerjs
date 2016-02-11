#!/usr/bin/env python

import threading
from subprocess import Popen, PIPE
from optparse import OptionParser
import json
from urlparse import urlparse
from collections import OrderedDict

from . import thread


PHANTOMJS = './node_modules/.bin/phantomjs'
LINKCHECKERJS = 'jslib/linkchecker.js'


def get_domain(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc


class Linkchecker(object):

    def __init__(self, pool, ignore_ssl_errors=False):
        self.pool = pool
        # Option passed to phantomjs
        self.ignore_ssl_errors = ignore_ssl_errors

        self.__checkLock = threading.Condition(threading.Lock())
        self.checked_urls = set()
        self.queued_urls = set()
        self.results = OrderedDict()
        self.errored_urls = {}
        self.depth = 0

    def check(self, url, domain):
        cmd = [PHANTOMJS]
        if self.ignore_ssl_errors is True:
            cmd += ['--ignore-ssl-errors=yes']
        cmd += [LINKCHECKERJS]
        if domain != get_domain(url):
            cmd += ['--url-only']
        cmd += [url]

        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = process.communicate()
        if process.returncode != 0:
            self.errored_urls[url] = stdout
            return False

        try:
            result = json.loads(stdout)
        except:
            # TODO: add logging
            pass
        self.checked_urls.add(url)
        self.perform(url, domain, result)

    def filter_urls(self, urls):
        self.__checkLock.acquire()
        try:
            urls -= self.checked_urls
            urls -= self.queued_urls
            self.queued_urls |= urls
            return urls
        finally:
            self.__checkLock.release()

    def perform(self, url, domain, result):
        self.results[url] = result
        urls = self.filter_urls(set(result['urls']))
        if self.depth < 2:
            self.depth += 1
            for u in urls:
                self.pool.add_task(self.check, url=u, domain=domain)


def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="Urls list", metavar="FILE")
    parser.add_option("-i", "--ignore-ssl-errors", action="store_true",
                      dest="ignore_ssl_errors",
                      help="Ignore ssl errors for self signed certificate")
    (options, args) = parser.parse_args()

    if options.filename is None and not args:
        raise Exception('Filename required')

    # Create a pool
    pool = thread.ThreadPool(20)

    linkchecker = Linkchecker(
        pool,
        ignore_ssl_errors=options.ignore_ssl_errors)

    urls = []
    if options.filename:
        with open(options.filename, 'r') as f:
            urls = [url for url in f.readlines()]
    else:
        urls = args

    for url in urls:
        url = url.strip()
        domain = get_domain(url)
        pool.add_task(linkchecker.check, url=url, domain=domain)

    pool.join_all()

    with open('data.json', 'w') as f:
        json.dump(linkchecker.results, f)


if __name__ == "__main__":
    main()
