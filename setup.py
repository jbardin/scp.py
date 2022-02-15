#!/usr/bin/env python

import io
import os
from setuptools import setup


# Need to specify encoding for PY3
with io.open('README.rst', encoding='utf-8') as fp:
    description = fp.read()
setup(
        name = 'scp',
        version = '0.14.3',
        author = 'James Bardin',
        author_email = 'j.bardin@gmail.com',
        maintainer="Remi Rampin",
        maintainer_email='remi@rampin.org',
        license = 'LGPL-2.1-or-later',
        url = 'https://github.com/jbardin/scp.py',
        description='scp module for paramiko',
        long_description=description,
        py_modules = ['scp'],
        install_requires = ['paramiko'],
        keywords=['paramiko', 'ssh', 'scp', 'transfer'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Internet',
        ],
)
