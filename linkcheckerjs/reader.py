#!/usr/bin/env python

from optparse import OptionParser

import json
from urlparse import urlparse


DEBUG = 3
INFO = 2
WARNING = 1
ERROR = 0

LEVELS = [DEBUG, INFO, WARNING, ERROR]


def get_scheme(url):
    return urlparse(url).scheme


def dict_to_str(dic, indent=0):
    keys = dic.keys()

    length = max(map(lambda k: len(k), keys))
    s = []
    for key in sorted(keys):
        value = dic[key]
        if value is None:
            continue
        formatted_key = '%% -%is :' % length
        sub = ' ' * indent
        sub += formatted_key % key
        sub += unicode(dic[key])
        s.append(sub)

    return '\n'.join(s)


def get_display_level(dic):
    if dic['status_code'] == 200:
        return DEBUG

    if dic['status_code'] == 302:
        return INFO

    if dic['status_code'] == 301:
        return WARNING

    return ERROR


class Page(object):

    def __init__(self, url, result, pages):
        self.url = url
        self.pages = pages
        self.result = result['page']
        self.resources = result['resources']
        self.urls = result['urls']
        self.check_unsecure()

    def check_unsecure(self):

        for res in self.resources:
            if res['status_code'] and get_scheme(res['url']) == 'https':
                # TODO: can we have url starting with '//'
                if get_scheme(res['response_url']) != 'https':
                    res['status'] = '---'.join(['Unsecure resources',
                                               str(res['status_code']),
                                               res['status']])
                    # Find a good status code
                    res['status_code'] = 500

    def display(self, level):
        s = []

        resources = []
        for res in self.resources:
            if get_display_level(res) <= level:
                resources.append(dict_to_str(res, 8))
                resources.append('')

        if resources:
            s.append('    Resources:')
            s.extend(resources)

        urls = []
        for url in self.urls:
            if url in self.pages:
                if get_display_level(self.pages[url].result) <= level:
                    urls.append(dict_to_str(self.pages[url].result, 8))
                    urls.append('')
        if urls:
            s.append('    Links:')
            s.extend(urls)

        if not urls and not resources:
            if get_display_level(self.result) > level:
                return None

        s.insert(0, dict_to_str(self.result, 4))
        s.insert(0, self.url)

        s.append('')
        s.append('')
        return '\n'.join(s)

    def __unicode__(self):
        return self.display(DEBUG)


def main():
    parser = OptionParser()
    parser.add_option("-l", "--log-level", type="int", dest="log_level",
                      help="linkcheckerjs log level")
    (options, args) = parser.parse_args()

    if options.log_level not in LEVELS:
        level = ERROR
    else:
        level = options.log_level

    data = json.load(open('data.json'))
    urls = data['urls']
    results = data['results']

    pages = {}
    for url in results.keys():
        page = Page(url, results[url], pages)
        pages[url] = page

    page_objects = pages.values()

    # TODO: perhaps we want to display url from urls first
    for page in page_objects:
        error = page.display(level)
        if error:
            print error


if __name__ == '__main__':
    main()
