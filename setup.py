#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'munin',
    version = '1.0.0',
    description = 'Framework for building Munin plugins',
    author = 'Samuel Stauffer',
    author_email = 'samuel@lefora.com',
    url = 'http://github.com/samuel/python-munin/tree/master',
    packages = ['munin'],
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
