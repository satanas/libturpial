#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from distutils.command.build import build
from libturpial import VERSION

LONG_DESCRIPTION = """
libturpial is a library that handles multiple microblogging protocols. It 
implements a lot of features and aims to support all the features for each 
protocol. This library is the backend used for Turpial.
"""

data_files=[
    ('./', ['ChangeLog', 'AUTHORS', 'COPYING']),
]

setup(name="libturpial",
    version=VERSION,
    description="Microblogging library",
    long_description=LONG_DESCRIPTION,
    author="Wil Alvarez",
    author_email="wil.alejandro@gmail.com",
    maintainer="Wil Alvarez",
    maintainer_email="wil.alejandro@gmail.com",
    url="http://github.com/Turpial/libturpial",
    download_url="http://github.com/Turpial/libturpial",
    license="GPLv3",
    keywords='twitter identi.ca microblogging api libturpial',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    include_package_data=True,
    packages=find_packages(),
    package_data={
        'libturpial': ['certs/*']
    },
    install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'oauth',
          'simplejson',
          'requests',
    ],
    data_files=data_files,
)
