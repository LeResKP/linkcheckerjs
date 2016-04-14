import os
import json
from optparse import OptionParser
from subprocess import Popen, PIPE

from .utils import standardize_url
from ..exc import PhantomjsException


path = os.path.abspath(__file__)
dir_path = os.path.dirname(os.path.dirname(path))

PHANTOMJS = os.path.join(dir_path, 'node_modules/phantomjs/bin/phantomjs')
LINKCHECKERJS = os.path.join(dir_path, 'jslib/linkchecker.js')


def parse_phantomjs_result(result, url, parent_url):
    """Parse the phantomjs result to returns data per page.

    We can have multiple pages when there is some redirect before having a real
    page
    """
    urls = result['urls']
    phantomjs_resources = result['resources']
    keys = phantomjs_resources.keys()
    page = None
    pages = []

    # Keys should be integer as string from 1
    for i in range(1, len(keys)+1):
        resource = phantomjs_resources[str(i)]
        response = resource['endReply']
        if not response:
            # Weird: An error occured during the request
            tmp_dict = {
                'checker': 'phantomjs',
                'url': standardize_url(url),
                'redirect_url': None,
                'status_code': 500,
                'status': 'No response',
                'parent_url': parent_url,
            }
        else:
            tmp_dict = {
                'checker': 'phantomjs',
                'url': response['url'],
                'redirect_url': response['redirectURL'],
                'status_code': response['status'],
                'status': response['statusText'],
                'parent_url': parent_url,
                # TODO: keep the raw_data when it will be needed
                # 'raw_data': resource,
            }

        if not page and response['status'] in [301, 302]:
            parent_url = response['url']
            pages += [tmp_dict]
        elif not page:
            parent_url = response['url']
            tmp_dict['resources'] = []
            page = tmp_dict
            pages += [page]
        else:
            page['resources'].append(tmp_dict)

    page['urls'] = urls
    return pages


def phantomjs_checker(url, parent_url=None, ignore_ssl_errors=False,
                      timeout=None):
    cmd = [PHANTOMJS]
    if ignore_ssl_errors is True:
        cmd += ['--ignore-ssl-errors=yes']
    cmd += [LINKCHECKERJS]
    cmd += [url]
    if timeout:
        cmd += [str(timeout)]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()
    if process.returncode != 0:
        raise PhantomjsException(unicode(stderr))

    dic = json.loads(stdout)
    return parse_phantomjs_result(dic, url, parent_url)


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print 'You must only give an url'
        exit(1)

    import pprint
    pprint.pprint(phantomjs_checker(args[0]))
