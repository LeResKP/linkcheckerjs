#!/usr/bin/env python

import requests
from optparse import OptionParser


def requests_checker(url, parent_url=None, ignore_ssl_errors=False):
    try:
        #TODO: better allow_redirects handling
        r = requests.head(url, allow_redirects=True, verify=not ignore_ssl_errors, timeout=5)
    except requests.Timeout:
        # TODO: better exception
        raise Exception('timeout')

    pages = []
    for p in r.history + [r]:
        pages += [{
            u'redirect_url': p.headers.get('location'),
            u'response_url': p.url,
            u'status': p.reason,
            u'status_code': p.status_code,
            u'url': url,
        }]
        url = p.headers.get('location') or p.url

    return pages


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print 'You must only give an url'
        exit(1)

    import pprint
    pprint.pprint(requests_checker(args[0]))
