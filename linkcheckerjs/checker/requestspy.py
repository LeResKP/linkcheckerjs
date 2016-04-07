#!/usr/bin/env python

import requests
from optparse import OptionParser

from ..exc import RequestsException

from .utils import standardize_url


def requests_checker(url, parent_url=None, ignore_ssl_errors=False,
                     timeout=None):
    try:
        r = requests.head(url, allow_redirects=True,
                          verify=not ignore_ssl_errors, timeout=timeout)
    except requests.Timeout, e:
        return [{
            'checker': 'requests',
            'url': standardize_url(e.request.url),
            'redirect_url': None,
            'status_code': 408,
            'status': 'Request Time-out',
            'parent_url': parent_url,
        }]
    except requests.exceptions.SSLError, e:
        # Same output as phantomsjs checker
        return [{
            'checker': 'requests',
            'url': standardize_url(e.request.url),
            'redirect_url': None,
            'status_code': None,
            'status': None,
            'parent_url': parent_url,
        }]
    except Exception, e:
        raise RequestsException(e)

    pages = []
    for p in r.history + [r]:
        pages += [{
            'checker': 'requests',
            'url': standardize_url(p.url),
            'redirect_url': p.headers.get('location'),
            'status_code': p.status_code,
            'status': p.reason,
            'parent_url': parent_url,
        }]

        parent_url = standardize_url(p.url)

    return pages


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print 'You must only give an url'
        exit(1)

    import pprint
    pprint.pprint(requests_checker(args[0]))
