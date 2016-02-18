#!/usr/bin/env python

import os
import re
import json
import logging
import requests
import threading

from urlparse import urlparse
from optparse import OptionParser
from subprocess import Popen, PIPE
from collections import OrderedDict

from . import thread

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(thread)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
log.addHandler(handler)


PHANTOMJS = os.path.join(dir_path, 'node_modules/phantomjs/bin/phantomjs')
LINKCHECKERJS = os.path.join(dir_path, 'jslib/linkchecker.js')


class CheckerException(Exception):
    pass

class PhantomjsException(CheckerException):
    pass

class RequestException(CheckerException):
    pass


def phantomjs_checker(url, ignore_ssl_errors=False, url_only=False):
    cmd = [PHANTOMJS]
    if ignore_ssl_errors is True:
        cmd += ['--ignore-ssl-errors=yes']
    cmd += [LINKCHECKERJS]
    if url_only:
        cmd += ['--url-only']
    cmd += [url]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()
    if process.returncode != 0:
        raise PhantomjsException('Bad return code %i:\n%s\n %s' % (
            process.returncode, stdout, stderr))

    return json.loads(stdout)


def requests_checker(url, ignore_ssl_errors=False):
    try:
        #TODO: better allow_redirects handling
        r = requests.head(url, allow_redirects=False, verify=not ignore_ssl_errors, timeout=5)
    except requests.Timeout:
        raise RequestException('timeout')

    return {
        u'page': {
            u'redirect_url': r.headers.get('location'),
            u'response_url': r.url,
            u'status': r.reason,
            u'status_code': r.status_code,
            u'url': url,
        },
        u'resources': [],
        u'urls': [],
    }


class Linkchecker(object):

    def __init__(self, phantom_pool, request_pool, ignore_ssl_errors=False,
                 ignore_url_patterns=None, domains=None, maxdepth=None):
        self.phantom_pool = phantom_pool
        self.request_pool = request_pool
        # Option passed to phantomjs
        self.ignore_ssl_errors = ignore_ssl_errors

        self.ignored_urls_regex = set(re.compile(p) for p in ignore_url_patterns)
        self.valid_domains = domains
        self.maxdepth = (maxdepth is None) and -1 or maxdepth

        self.__checkLock = threading.Condition(threading.Lock())
        self.results = OrderedDict()
        self.errored_urls = {}

        # Security to not crawl all the web
        self.max_nb_urls = 50000

    def check(self, url, depth=0):
        try:
            result = phantomjs_checker(url, self.ignore_ssl_errors)
            result.update({
                'crawler': 'PHANTOM',
            })
            self.results[url] = result
            self.feed_result(result, depth+1)
        except CheckerException as e:
            self.errored_urls[url] = e

    def quick_check(self, url, reason):
        try:
            result = requests_checker(url, self.ignore_ssl_errors)
            result.update({
                'crawler': 'REQUESTS',
                'quick': reason,
            })
            self.results[url] = result
        except CheckerException as e:
            self.errored_urls[url] = e

    def feed_result(self, result, new_depth):
        urls_to_check = self.filter_ignore_urls_patterns(result['urls'])

        # Feed discovered url to the checker
        self.__checkLock.acquire()
        try:
            for next_url in urls_to_check:
                if next_url in self.results:
                    continue
                self.results[next_url] = None
                self.schedule(next_url, new_depth)
        finally:
            self.__checkLock.release()

    def schedule(self, url, new_depth=0):
        if urlparse(url).hostname not in self.valid_domains:
            self.request_pool.add_task(self.quick_check, url=url, reason='OTHER_DOMAIN')
        elif new_depth > self.maxdepth:
            self.request_pool.add_task(self.quick_check, url=url, reason='TOO_FAR_IN_OUR_DOMAINS')
        else:
            self.phantom_pool.add_task(self.check, url=url, depth=new_depth)

    def filter_ignore_urls_patterns(self, urls):
        # TODO: improve with domains
        return (u for u in urls
            if not any(r.search(u) for r in self.ignored_urls_regex))

    def wait(self):
        self.request_pool.join_all()
        self.phantom_pool.join_all()


def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="Urls list", metavar="FILE")
    parser.add_option("-i", "--ignore-ssl-errors", action="store_true",
                      dest="ignore_ssl_errors",
                      help="Ignore ssl errors for self signed certificate")
    parser.add_option("-d", "--max-depth", dest="maxdepth", type="int")
    parser.add_option("-t", "--thread", dest="thread", type="int", default=8)
    parser.add_option("--ignore-url-pattern", action="append",
                      dest="ignore_url_patterns",
                      help="Pattern to ignore when crawling pages")
    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose")
    (options, args) = parser.parse_args()

    if options.filename is None and not args:
        raise Exception('Filename required')

    if options.verbose:
        handler.setLevel(logging.DEBUG)
        thread.handler.setLevel(logging.DEBUG)


    if options.filename:
        with open(options.filename, 'r') as f:
            urls = [url for url in f.readlines()]
    else:
        urls = args

    # Create a pool
    log.debug('Starting pool with %i threads' % options.thread)
    phantom_pool = thread.ThreadPool(options.thread)
    request_pool = thread.ThreadPool(options.thread * 5)

    linkchecker = Linkchecker(
        phantom_pool,
        request_pool,
        ignore_url_patterns=options.ignore_url_patterns,
        ignore_ssl_errors=options.ignore_ssl_errors,
        maxdepth=options.maxdepth,
        domains=set(urlparse(url).hostname for url in urls),
    )

    for url in urls:
        url = url.strip()
        linkchecker.schedule(url)


    linkchecker.wait()

    with open('data.json', 'w') as f:
        json.dump(linkchecker.results, f)


if __name__ == "__main__":
    main()
