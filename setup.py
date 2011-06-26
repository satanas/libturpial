#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import re

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from distutils.command.build import build
from libturpial.api.common import VERSION

LONG_DESCRIPTION = """
Turpial API is a library that allow programs to handle multiple microblogging 
accounts in services like Twitter and Identi.ca. Is light, fully featured and
easy to use.
"""

# TODO: Maybe find some better ways to do this
data_files=[
    ('share/doc/turpial_api', ['ChangeLog', 'AUTHORS', 'COPYING']),
]

setup(name="turpialapi",
    version=VERSION,
    description="Turpial API library",
    long_description=LONG_DESCRIPTION,
    author="Wil Alvarez",
    author_email="wil.alejandro@gmail.com",
    maintainer="Wil Alvarez",
    maintainer_email="wil.alejandro@gmail.com",
    url="http://turpial.org.ve",
    download_url="http://turpial.org.ve/downloads",
    license="GPLv3",
    keywords='twitter identi.ca microblogging turpial',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages=find_packages(),
    cmdclass={
        'build': build,
    },
    data_files=data_files,
)
