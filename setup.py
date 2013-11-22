#!/usr/bin/env python

import os
from setuptools import setup

setup(
        name = 'scp',
        version = '0.6.2',
        author = 'James Bardin',
        author_email = 'j.bardin@gmail.com',
        license = 'LGPL',
        url = 'https://github.com/jbardin/scp.py.git',
        description='scp module for paramiko',
        py_modules = ['scp'],
        install_requires = ['paramiko'],
)
