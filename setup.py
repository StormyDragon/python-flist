#!/usr/bin/env python

from distutils.core import setup
import sys

py_version = sys.version_info[:2]

additional_requirements = []
if py_version == (3, 3):
    additional_requirements.append('asyncio')

setup(name='Python-flist',
      version='0.1.0',
      author='StormyDragon',
      author_email='stormy.pypi@stormweyr.dk',
      description='Python module for interacting with the f-list website.',
      url='https://github.com/StormyDragon/python-flist',
      packages=['flist',],
      keywords=['flist',],
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "License :: OSI Approved :: BSD License",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Operating System :: OS Independent",
          "Topic :: Games/Entertainment :: Role-Playing",
          "Topic :: Communications :: Chat",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      requires=[
          'websockets',
          'aiohttp (>=0.4.4)',
      ] + additional_requirements,
      provides=[
          'flist',
      ],
      long_description= """
Framework for interacting with the F-list website
-------------------------------------------------


This version requires Python 3.3 with asyncio, or Python 3.4
websockets and aiohttp are also used (I kinda expect these kinds of modules to return to the standard library).""",
)


