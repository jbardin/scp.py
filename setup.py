#!/usr/bin/env python

import io
import os
from setuptools import setup


# Need to specify encoding for PY3
with io.open('README.rst', encoding='utf-8') as fp:
    description = fp.read()
setup(
        name = 'scp',
        version = '0.10.0',
        author = 'James Bardin',
        author_email = 'j.bardin@gmail.com',
        license = 'LGPL',
        url = 'https://github.com/jbardin/scp.py',
        description='scp module for paramiko',
        long_description=description,
        py_modules = ['scp'],
        install_requires = ['paramiko'],
)
