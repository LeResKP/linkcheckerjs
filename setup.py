import os
import json
from setuptools import setup, find_packages
from distutils.command.build import build as _build

import subprocess

version = '0.0'


class NpmInstall(_build):

    def run(self):
        package = json.load(open('package.json'))
        packages = []
        for name, version in package.get('dependencies', {}).items():
            packages.append('%s@%s' % (name, version))
        print 'Installing node packages: %s' % ' '.join(packages)
        p = subprocess.Popen(["npm install --prefix build/lib/linkcheckerjs/ %s" % ' '.join(packages)], shell=True)
        p.communicate()
        _build.run(self)


setup(
    cmdclass={'build': NpmInstall},
    name='linkcheckerjs',
    version=version,
    description="",
    long_description="""\
    """,
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Aur\xc3\xa9lien Matouillot',
    author_email='a.matouillot@gmail.com',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [console_scripts]
    linkcheckerjs = linkcheckerjs.checker:main
    linkreaderjs = linkcheckerjs.reader:main
    """,
)
