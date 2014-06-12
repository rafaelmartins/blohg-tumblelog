#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    setup.py
    ~~~~~~~~

    :copyright: (c) 2014 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from setuptools import setup
import os

cwd = os.path.dirname(os.path.abspath(__file__))


setup(
    name='blohg-tumblelog',
    version='0.2',
    license='GPL-2',
    description=('A blohg extension with reStructuredText directives to run '
                 'a tumblelog'),
    long_description=open(os.path.join(cwd, 'README.rst')).read(),
    author='Rafael Goncalves Martins',
    author_email='rafael@rafaelmartins.eng.br',
    url='http://blohg.org/',
    platforms='any',
    py_modules=['blohg_tumblelog'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'blohg>=0.12',
        'Pygments',
        'pyoembed',
        'beautifulsoup4',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ],
)
