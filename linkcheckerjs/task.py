#!/usr/bin/env python

import signal
from subprocess import Popen, PIPE
from optparse import OptionParser
import json

from . import thread


pool = None


def signal_handler(signal, frame):
    if not pool:
        exit(0)
    pool.joinAll(waitForTasks=False, waitForThreads=True)

signal.signal(signal.SIGINT, signal_handler)


def linkchecker_task(data):
    cmd = ['./node_modules/.bin/phantomjs']
    if data['ignore_ssl_errors'] is True:
        cmd += ['--ignore-ssl-errors=yes']
    cmd += ['lib/linkchecker.js']
    if data['log_level'] is not None:
        cmd += ['--log-level=%i' % data['log_level']]
    cmd += [data['url']]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()
    dic = json.loads(stdout)
    print 'dic', dic


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
    global pool
    pool = thread.ThreadPool(20)

    if options.filename:
        with open(options.filename, 'r') as f:
            for url in f.readlines():
                pool.queueTask(linkchecker_task, {
                    'url': url.strip(),
                    'ignore_ssl_errors': options.ignore_ssl_errors,
                    'log_level': options.log_level})
    else:
        for url in args:
            pool.queueTask(linkchecker_task, {
                'url': url.strip(),
                'ignore_ssl_errors': options.ignore_ssl_errors,
                'log_level': options.log_level})

    # When all tasks are finished, allow the threads to terminate
    pool.joinAll()

if __name__ == "__main__":
    main()
