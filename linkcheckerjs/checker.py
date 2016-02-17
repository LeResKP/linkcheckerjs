#!/usr/bin/env python

import os
import threading
from subprocess import Popen, PIPE
from optparse import OptionParser
import json
from urlparse import urlparse
from collections import OrderedDict

from . import thread
import re

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

PHANTOMJS = os.path.join(dir_path, 'node_modules/phantomjs/bin/phantomjs')
LINKCHECKERJS = os.path.join(dir_path, 'jslib/linkchecker.js')


RE_CACHE = {}


class PhantomjsException(Exception):
    pass


def phantomjs_checker(url, domain, ignore_ssl_errors=False):
    cmd = [PHANTOMJS]
    if ignore_ssl_errors is True:
        cmd += ['--ignore-ssl-errors=yes']
    cmd += [LINKCHECKERJS]
    if domain != get_hostname(url):
        cmd += ['--url-only']
    cmd += [url]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()
    if process.returncode != 0:
        raise PhantomjsException('Bad return code %i:\n%s\n %s' % (
            process.returncode, stdout, stderr))

    return json.loads(stdout)


def get_hostname(url):
    parsed_uri = urlparse(url)
    return parsed_uri.hostname


def match_pattern(pattern, url):
    global RE_CACHE
    if pattern not in RE_CACHE:
        RE_CACHE[pattern] = re.compile(pattern)

    regex = RE_CACHE[pattern]
    return regex.search(url)


class Linkchecker(object):

    def __init__(self, pool, ignore_ssl_errors=False,
                 ignore_url_patterns=None, maxdepth=None):
        self.pool = pool
        # Option passed to phantomjs
        self.ignore_ssl_errors = ignore_ssl_errors

        self.ignore_url_patterns = ignore_url_patterns
        self.maxdepth = maxdepth
        self.__checkLock = threading.Condition(threading.Lock())
        self.checked_urls = set()
        self.queued_urls = set()
        self.results = OrderedDict()
        self.errored_urls = {}
        self.max_nb_urls = 200

    def check(self, url, domain, depth=0):
        try:
            result = phantomjs_checker(url, domain, self.ignore_ssl_errors)
        except Exception, e:
            self.errored_urls[url] = e
            return False

        self.checked_urls.add(url)
        self.results[url] = result
        self.perform(url, domain, result, depth)

    def filter_urls(self, urls):
        self.__checkLock.acquire()
        try:
            # TODO: we should either remove errored_urls or retry to get it
            # then if okay remove it from errored_urls
            urls -= self.checked_urls
            urls -= self.queued_urls
            self.queued_urls |= urls
            return urls
        finally:
            self.__checkLock.release()

    def filter_ignore_urls_patterns(self, urls):
        if not self.ignore_url_patterns:
            return urls

        return set([
            u for u in urls
            if not any([match_pattern(p, u) for p in
                        self.ignore_url_patterns])])

    def perform(self, url, domain, result, depth):
        if self.maxdepth is not None and depth >= self.maxdepth:
            return False

        urls = self.filter_ignore_urls_patterns(set(result['urls']))
        urls = self.filter_urls(urls)
        if len(self.checked_urls) < self.max_nb_urls:
            for u in urls:
                self.pool.add_task(self.check, url=u, domain=domain,
                                   depth=depth+1)


def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="Urls list", metavar="FILE")
    parser.add_option("-i", "--ignore-ssl-errors", action="store_true",
                      dest="ignore_ssl_errors",
                      help="Ignore ssl errors for self signed certificate")
    parser.add_option("-d", "--max-depth", dest="maxdepth", type="int")
    parser.add_option("--ignore-url-pattern", action="append",
                      dest="ignore_url_patterns",
                      help="Pattern to ignore when crawling pages")
    (options, args) = parser.parse_args()

    if options.filename is None and not args:
        raise Exception('Filename required')

    # Create a pool
    pool = thread.ThreadPool(20)

    linkchecker = Linkchecker(
        pool,
        ignore_url_patterns=options.ignore_url_patterns,
        ignore_ssl_errors=options.ignore_ssl_errors,
        maxdepth=options.maxdepth,
    )

    urls = []
    if options.filename:
        with open(options.filename, 'r') as f:
            urls = [url for url in f.readlines()]
    else:
        urls = args

    for url in urls:
        url = url.strip()
        domain = get_hostname(url)
        pool.add_task(linkchecker.check, url=url, domain=domain)

    pool.join_all()

    with open('data.json', 'w') as f:
        json.dump(linkchecker.results, f)


if __name__ == "__main__":
    main()
