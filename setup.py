#!/usr/bin/env python

import sys
from os.path import exists
from setuptools import setup, find_packages


setup(name='cityscrape',
      version='0.0.1',
      description='This package scrapes city websites.',
      author='Vidal Anguiano Jr.',
      url='ssh://github.com/CityBaseInc/cityscrape',
      maintainer_email='vanguiano@thecitybase.com',
      packages=['cityscrape'],
      long_description=open('README.md').read() if exists('README.md') else ''
      )
