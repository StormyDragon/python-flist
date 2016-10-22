#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

requirements = [
    "aiohttp>=0.20",
]

setup(name='Python-flist',
      version='0.1.0',
      author='StormyDragon',
      author_email='stormy.pypi@stormweyr.dk',
      description='Python module for interacting with the f-list website.',
      url='https://github.com/StormyDragon/python-flist',
      packages=find_packages(exclude=['examples']),
      keywords=['flist'],
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "License :: OSI Approved :: BSD License",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.5",
          "Operating System :: OS Independent",
          "Topic :: Games/Entertainment :: Role-Playing",
          "Topic :: Communications :: Chat",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      install_requires=requirements,
      provides=[
          'flist',
      ],
      long_description="""
Framework for interacting with the F-list website
-------------------------------------------------

Python module for F-List

This module requires python 3.5
For HTTPS and websockets the aiohttp module is used.
""",
      )
