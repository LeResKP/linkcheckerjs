import os
import json
from optparse import OptionParser
from subprocess import Popen, PIPE


path = os.path.abspath(__file__)
dir_path = os.path.dirname(os.path.dirname(path))

PHANTOMJS = os.path.join(dir_path, 'node_modules/phantomjs/bin/phantomjs')
LINKCHECKERJS = os.path.join(dir_path, 'jslib/linkchecker2.js')


def phantomjs_checker(url, parent_url=None,
                      ignore_ssl_errors=False):
    cmd = [PHANTOMJS]
    if ignore_ssl_errors is True:
        cmd += ['--ignore-ssl-errors=yes']
    cmd += [LINKCHECKERJS]
    cmd += [url]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()
    if process.returncode != 0:
        # TODO: better exception
        raise Exception('Bad return code %i:\n%s\n %s' % (
            process.returncode, stdout, stderr))

    dic = json.loads(stdout)

    pages = []
    page_loaded = False
    # TODO: make sure we have some keys
    urls = dic['urls']
    dic = dic['resources']
    for i in range(1, len(dic.keys())+1):
        res = dic[str(i)]
        res['parent_url'] = parent_url
        res['checker'] = 'phantomjs'
        # TODO: do we really need default ?
        res['urls'] = []
        if 'url' in res:
            raise Exception('Strange??')
        res['url'] = res['endReply']['url']
        # TODO: write tests to be sure phantomjs script always return something
        if not page_loaded and res['endReply']['status'] in [301, 302]:
            parent_url = res['endReply']['url']
            pages += [res]
        elif not page_loaded:
            page_loaded = True
            res['resources'] = []
            pages += [res]
        else:
            pages[-1]['resources'].append(res)

    pages[-1]['urls'] = urls
    return pages


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print 'You must only give an url'
        exit(1)

    import pprint
    pprint.pprint(phantomjs_checker(args[0]))
